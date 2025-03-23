from datetime import timedelta

import requests
from django.db.models import Sum, Max, Avg, ExpressionWrapper, fields, F
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import MinecraftServer, MinecraftPlayerSession, MinecraftServerOnline, MinecraftPlayer


def index(request):
    return render(request, 'index.html')


def servers(request):
    servers = MinecraftServer.objects.all()
    return render(request, 'servers.html', {'servers': servers})


def remove_server(request, ip):
    if request.method == 'POST':
        MinecraftServer.objects.filter(ip=ip).delete()
    return redirect('servers')


def watcher(request):
    return render(request, 'watcher.html')


def add_server(request):
    if request.method == 'POST':
        MinecraftServer.objects.create(
            ip=request.POST['ip'],
            port=request.POST['port'],
            motd=request.POST['motd'],
            version=request.POST['version'],
            max_players=request.POST['max_players'],
            online_mode=request.POST.get('online_mode') == 'on',
            core=request.POST.get('core', 'Unknown')
        )
        return redirect('servers')
    return render(request, 'watcher.html')


def analytics(request):
    total_servers = MinecraftServer.objects.count()
    servers = MinecraftServer.objects.all()

    # Player Analytics
    total_players = MinecraftPlayer.objects.count()
    total_play_time = MinecraftPlayer.objects.aggregate(
        total_play_time=Sum('play_time')
    )['total_play_time'] or 0

    # Recent Player Sessions (last 7 days)
    recent_sessions = MinecraftPlayerSession.objects.filter(
        join_time__gte=timezone.now() - timedelta(days=7)
    )

    # Server Population Analytics
    server_population_analytics = []
    online_history_data = []  # Data for the graph
    for server in servers:
        # Fetch online history for the last 24 hours
        online_history = MinecraftServerOnline.objects.filter(
            server=server,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('timestamp')

        peak_online = online_history.aggregate(
            peak_online=Max('online')
        )['peak_online'] or 0

        avg_online = online_history.aggregate(
            avg_online=Avg('online')
        )['avg_online'] or 0

        # Player session analytics for this server (last 7 days)
        server_sessions = MinecraftPlayerSession.objects.filter(
            server=server,
            join_time__gte=timezone.now() - timedelta(days=7)
        )

        server_analytics = {
            'server': server,
            'peak_online': peak_online,
            'avg_online': round(avg_online, 2),
            'total_sessions': server_sessions.count(),
            'total_session_duration': sum(
                ((session.leave_time or timezone.now()) - session.join_time).total_seconds() / 60
                for session in server_sessions
            )
        }
        server_population_analytics.append(server_analytics)

        # Prepare online history data for the chart (last 24 hours)
        online_history_data.append({
            'ip': server.ip,
            'port': server.port,
            'history': [
                {'timestamp': entry.timestamp.isoformat(), 'online': entry.online}
                for entry in online_history
            ]
        })

    # Top 10 Players by Playtime
    top_players = MinecraftPlayer.objects.annotate(
        total_play_hours=ExpressionWrapper(
            F('play_time') / 60,
            output_field=fields.FloatField()
        )
    ).order_by('-total_play_hours')[:10]

    context = {
        'total_servers': total_servers,
        'total_players': total_players,
        'total_play_time_hours': total_play_time / 60,
        'server_population_analytics': server_population_analytics,
        'top_players': top_players,
        'recent_sessions_count': recent_sessions.count(),
        'online_history_data': online_history_data,
    }

    return render(request, 'analytics.html', context)
