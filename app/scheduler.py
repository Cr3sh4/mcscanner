import logging
from typing import Dict, Any, List, Optional

import requests
from django.db import transaction
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler

from .models import (
    MinecraftServer,
    MinecraftPlayer,
    MinecraftServerOnline,
    MinecraftPlayerSession
)

# Configure logging
logger = logging.getLogger(__name__)

# Configuration can be moved to Django settings
TRACKING_INTERVAL_MINUTES = 1
API_TIMEOUT = 5
API_BASE_URL = 'https://api.mcsrvstat.us/3'


class MinecraftServerTracker:
    """
    Class for tracking Minecraft servers and their players
    Tracking:
    - Server online player count
    - Player sessions
    - Player playtime
    """

    @classmethod
    def fetch_server_data(cls, server: MinecraftServer) -> Optional[Dict[str, Any]]:
        """
        Fetch server data from the API
        :param server: 
        :return:
        """
        api_url = f'{API_BASE_URL}/{server.ip}:{server.port}'
        try:
            response = requests.get(api_url, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # Validate API response
            if not data or data.get('online') is False:
                # Check for specific error conditions
                debug_info = data.get('debug', {})
                error_details = debug_info.get('error', {})

                if error_details:
                    logger.warning(f"Server {server.ip}:{server.port} connection failed. Errors: {error_details}")

                return None

            return data

        except requests.RequestException as e:
            logger.error(f"API request failed for {server.ip}:{server.port}. Error: {e}")
            return None
        except ValueError as e:
            logger.error(f"JSON parsing error for {server.ip}:{server.port}. Error: {e}")
            return None

    @classmethod
    @transaction.atomic
    def track_server_online_status(cls, server: MinecraftServer, data: Dict[str, Any]) -> None:
        """
        Track server online status
        :param server:
        :param data:  
        :return:
        """
        try:
            online_count = data.get('players', {}).get('online', 0)
            MinecraftServerOnline.objects.create(
                server=server,
                online=online_count
            )
            logger.info(f"Recorded online status for {server.ip}: {online_count} players")
        except Exception as e:
            logger.error(f"Error tracking online status for {server.ip}: {e}")

    @classmethod
    @transaction.atomic
    def manage_player_sessions(cls, server: MinecraftServer, data: Dict[str, Any]) -> None:
        """
        Manage player sessions
        :param server:
        :param data:
        """
        try:
            current_players = data.get('players', {}).get('list', [])
            current_nicknames = {player['name'] for player in current_players}

            # Close sessions for disconnected players
            cls._close_inactive_sessions(server, current_nicknames)

            # Open new sessions for new players
            cls._open_new_sessions(server, current_players)

        except Exception as e:
            logger.error(f"Error managing player sessions for {server.ip}: {e}")

    @classmethod
    def _close_inactive_sessions(cls, server: MinecraftServer, current_nicknames: set) -> None:
        """
        Close sessions for disconnected players
        :param server:
        :param current_nicknames:
        :return:
        """
        open_sessions = MinecraftPlayerSession.objects.filter(
            server=server,
            leave_time__isnull=True
        )

        sessions_to_update = [
            session for session in open_sessions
            if session.player.nickname not in current_nicknames
        ]

        for session in sessions_to_update:
            session.leave_time = timezone.now()
            session.save()

    @classmethod
    def _open_new_sessions(cls, server: MinecraftServer, current_players: List[Dict[str, str]]) -> None:
        """
        Open new sessions for new players
        :param server:
        :param current_players:
        :return:
        """
        for player_data in current_players:
            nickname = player_data['name']

            # Find or create player
            player, _ = MinecraftPlayer.objects.get_or_create(
                nickname=nickname,
                ip=server.ip,
                defaults={}
            )

            # Check if an active session already exists
            existing_active_session = MinecraftPlayerSession.objects.filter(
                player=player,
                server=server,
                leave_time__isnull=True
            ).first()

            # Create a new session if no active session exists
            if not existing_active_session:
                MinecraftPlayerSession.objects.create(
                    player=player,
                    server=server
                )

    @classmethod
    def update_player_playtime(cls, server: MinecraftServer, data: Dict[str, Any]) -> None:
        """
        Update player playtime
        :param server:
        :param data:
        :return:
        """
        try:
            online_players = data.get('players', {}).get('list', [])

            for player_data in online_players:
                nickname = player_data['name']

                # Update or create player with incremented playtime
                player, created = MinecraftPlayer.objects.get_or_create(
                    ip=server.ip,
                    nickname=nickname,
                    defaults={'play_time': TRACKING_INTERVAL_MINUTES}
                )

                if not created:
                    player.play_time += TRACKING_INTERVAL_MINUTES
                    player.save()

                logger.debug(f"Updated playtime for {nickname} on {server.ip}")

        except Exception as e:
            logger.error(f"Error updating player playtime for {server.ip}: {e}")

    @classmethod
    def watch_players_session(cls) -> None:
        """
        Watch players session
        Tracking player sessions
        :return:
        """
        logger.info(f"[{timezone.now()}] Running watch players session...")

        servers = MinecraftServer.objects.all()

        for server in servers:
            try:
                # Fetch server data
                server_data = cls.fetch_server_data(server)

                if server_data:
                    # Track server online status
                    cls.track_server_online_status(server, server_data)

                    # Manage player sessions
                    cls.manage_player_sessions(server, server_data)

                    # Update player playtime
                    cls.update_player_playtime(server, server_data)

            except requests.RequestException as e:
                logger.error(f"Error fetching server data for {server.ip}:{server.port}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing server {server.ip}:{server.port}: {e}")

    @classmethod
    def run_tracking(cls) -> None:
        """
        Run task scheduler
        :return:
        """
        logger.info("Starting Minecraft server tracking...")
        cls.watch_players_session()


def start_scheduler() -> None:
    """
    Initialize scheduler
    :return:
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        MinecraftServerTracker.run_tracking,
        'interval',
        minutes=TRACKING_INTERVAL_MINUTES
    )

    try:
        scheduler.start()
        logger.info("Minecraft server tracking scheduler started.")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


# Logging
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )