from flask import render_template, request, copy_current_request_context
from flask_socketio import emit, join_room, rooms, leave_room, close_room, disconnect

from config.celery import async_emit_msg
from config.common import app
from config.socket import socketio


def onEvents():
    pass


######################SocketIO#######################################

@app.route('/')
def sessions():
    return render_template('session.html')


@socketio.on('my_event')
def test_message(message):
    app.logger.info('#########my_event    {}#########'.format(message))
    async_emit_msg('my_response', {'data': message['data'], 'count': 'receive_count'}).delay()


@socketio.on('join')
def join(message):
    join_room(message['room'])
    app.logger.info('##### {} entered {}'.format(request.sid, message['room']))
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': 'receive_count'})


@socketio.on('leave')
def leave(message):
    leave_room(message['room'])
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': 'receive_count'})


@socketio.on('close_room')
def close(message):
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': 'receive_count'},
         room=message['room'])
    close_room(message['room'])


@socketio.on('my_room_event')
def send_room_message(message):
    emit('my_response',
         {'data': message['data'], 'count': 'receive_count'},
         room=message['room'])


@socketio.on('disconnect_request')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': 'receive_count'},
         callback=can_disconnect)


@socketio.on('connect')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('testroom')
def test_room():
    app.logger.info('#########testroom#########')
    # 只有room0收到了
    emit('room', request.sid + ' has entered the room.', room='room0')
    # 只有room0收到了
    emit('room', 'emit to all rooms', )
    # 未加入room也收到了
    emit('room', 'broadcast to all rooms', broadcast=True)
