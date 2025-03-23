from django.db import models
from django.utils import timezone

# Create your models here.

class MinecraftServer(models.Model):
    id = models.BigAutoField(primary_key=True)
    ip = models.CharField(max_length=255, unique=True)
    port = models.IntegerField()
    motd = models.TextField()
    version = models.CharField(max_length=64)
    max_players = models.IntegerField()
    online_mode = models.BooleanField()
    core = models.CharField(max_length=64, default='Unknown')

    def __str__(self):
        return f"{self.ip}:{self.port}"

class MinecraftServerOnline(models.Model):
    server = models.ForeignKey(MinecraftServer, on_delete=models.CASCADE)
    online = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.server} - {self.online} players"


class MinecraftPlayer(models.Model):
    ip = models.CharField(max_length=255)
    nickname = models.CharField(max_length=16, null=True)
    play_time = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nickname} ({self.ip})"

class MinecraftPlayerSession(models.Model):
    player = models.ForeignKey(MinecraftPlayer, on_delete=models.CASCADE)
    server = models.ForeignKey(MinecraftServer, on_delete=models.CASCADE)
    join_time = models.DateTimeField(auto_now_add=True)
    leave_time = models.DateTimeField(null=True)

    @property
    def duration(self):
        if self.leave_time:
            return self.leave_time - self.join_time
        return timezone.now() - self.join_time

    def __str__(self):
        return f"{self.player} on {self.server}"
