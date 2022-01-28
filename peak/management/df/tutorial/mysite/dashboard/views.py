from django.shortcuts import render, get_object_or_404
from . import xmpp

 

async def index(request):
    rooms = await xmpp.room_list()
    context = {'rooms': rooms}
    return render(request, 'dashboard/index.html', context)