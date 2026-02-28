import socketio
from typing import List, Optional
from dataclasses import dataclass
from .events import SocketEvent, UserConnectionStatus

@dataclass
class ConnectedUser:
    """Represents a connected user in a room"""
    username: str
    roomId: str
    status: UserConnectionStatus
    cursorPosition: int
    typing: bool
    socketId: str
    currentFile: Optional[str] = None
    userId: Optional[str] = None

# In-memory store (Replace with Redis for production scalability)
user_socket_map: List[ConnectedUser] = []

def get_users_in_room(room_id: str) -> List[ConnectedUser]:
    return [user for user in user_socket_map if user.roomId == room_id]

def get_room_id(socket_id: str) -> Optional[str]:
    for user in user_socket_map:
        if user.socketId == socket_id:
            return user.roomId
    return None

def get_user_by_socket_id(socket_id: str) -> Optional[ConnectedUser]:
    for user in user_socket_map:
        if user.socketId == socket_id:
            return user
    return None

def user_to_dict(user: ConnectedUser) -> dict:
    return {
        "username": user.username,
        "roomId": user.roomId,
        "status": user.status.value,
        "cursorPosition": user.cursorPosition,
        "typing": user.typing,
        "socketId": user.socketId,
        "currentFile": user.currentFile,
        "userId": user.userId
    }

def register_socket_handlers(sio: socketio.AsyncServer):
    """Register all socket event handlers"""
    global user_socket_map

    @sio.event
    async def connect(sid, environ):
        # We don't authenticate here yet, we wait for 'join_request'
        print(f"Client connected: {sid}")

    @sio.event
    async def disconnect(sid):
        global user_socket_map
        user = get_user_by_socket_id(sid)
        if not user:
            return
        
        room_id = user.roomId
        
        # Notify others
        await sio.emit(
            SocketEvent.USER_DISCONNECTED.value,
            {"user": user_to_dict(user)},
            room=room_id,
            skip_sid=sid
        )
        
        # Remove from map
        user_socket_map = [u for u in user_socket_map if u.socketId != sid]
        
        # Leave room
        sio.leave_room(sid, room_id)
        print(f"Client disconnected: {sid}")

    @sio.on(SocketEvent.JOIN_REQUEST.value)
    async def handle_join_request(sid, data):
        global user_socket_map
        room_id = data.get("roomId")
        username = data.get("username")
        user_id = data.get("userId") # Optional auth link
        
        print(f"Join Request: {username} -> {room_id}")

        # Basic validation
        if not room_id or not username:
            await sio.emit(SocketEvent.ERROR.value, {"message": "Invalid join request"}, room=sid)
            return

        # Create user
        user = ConnectedUser(
            username=username,
            roomId=room_id,
            status=UserConnectionStatus.ONLINE,
            cursorPosition=0,
            typing=False,
            socketId=sid,
            currentFile=None,
            userId=user_id
        )
        user_socket_map.append(user)
        
        # Join Socket.IO room
        await sio.enter_room(sid, room_id)
        
        # Notify OTHERS in the room
        await sio.emit(
            SocketEvent.USER_JOINED.value,
            {"user": user_to_dict(user)},
            room=room_id,
            skip_sid=sid
        )
        
        # Send ACCEPTANCE to the joining user, with list of current users
        current_users = [user_to_dict(u) for u in get_users_in_room(room_id)]
        await sio.emit(
            SocketEvent.JOIN_ACCEPTED.value,
            {"user": user_to_dict(user), "users": current_users},
            room=sid
        )

    # --- FILE STRUCTURE SYNC ---
    
    @sio.on(SocketEvent.SYNC_FILE_STRUCTURE.value)
    async def handle_sync_file_structure(sid, data):
        """Forward complete file tree to a specific socket (used on user join)"""
        target_sid = data.get("socketId")
        if target_sid:
            await sio.emit(
                SocketEvent.SYNC_FILE_STRUCTURE.value,
                {
                    "fileStructure": data.get("fileStructure"),
                    "openFiles": data.get("openFiles"),
                    "activeFile": data.get("activeFile"),
                },
                room=target_sid
            )

    # --- FILE EVENTS ---
    
    @sio.on(SocketEvent.FILE_CREATED.value)
    async def handle_file_created(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.FILE_CREATED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.FILE_UPDATED.value)
    async def handle_file_updated(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.FILE_UPDATED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.FILE_RENAMED.value)
    async def handle_file_renamed(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.FILE_RENAMED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.FILE_DELETED.value)
    async def handle_file_deleted(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.FILE_DELETED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    # --- DIRECTORY EVENTS ---

    @sio.on(SocketEvent.DIRECTORY_CREATED.value)
    async def handle_directory_created(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.DIRECTORY_CREATED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.DIRECTORY_UPDATED.value)
    async def handle_directory_updated(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.DIRECTORY_UPDATED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.DIRECTORY_RENAMED.value)
    async def handle_directory_renamed(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.DIRECTORY_RENAMED.value,
                data,
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.DIRECTORY_DELETED.value)
    async def handle_directory_deleted(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.DIRECTORY_DELETED.value,
                data,
                room=room_id,
                skip_sid=sid
            )
            
    # --- CHAT EVENTS ---
    
    @sio.on(SocketEvent.JOIN_CHAT.value)
    async def handle_join_chat(sid, data):
        """User joins a specific chat room (direct or team)"""
        chat_room_id = data.get("chatRoomId")
        if chat_room_id:
            await sio.enter_room(sid, f"chat_{chat_room_id}")
            print(f"User {sid} joined chat room: chat_{chat_room_id}")

    @sio.on(SocketEvent.LEAVE_CHAT.value)
    async def handle_leave_chat(sid, data):
        chat_room_id = data.get("chatRoomId")
        if chat_room_id:
            sio.leave_room(sid, f"chat_{chat_room_id}")
            print(f"User {sid} left chat room: chat_{chat_room_id}")
            
    @sio.on(SocketEvent.SEND_MESSAGE.value)
    async def handle_send_message(sid, data):
        """
        Broadcasting a message to a specific chat room.
        Data should contain: { 'chatRoomId': '...', 'message': {...} }
        """
        chat_room_id = data.get("chatRoomId")
        if chat_room_id:
            await sio.emit(
                SocketEvent.RECEIVE_MESSAGE.value,
                data.get("message"), 
                room=f"chat_{chat_room_id}",
                skip_sid=sid
            )

    # --- TYPING / CURSOR EVENTS ---

    @sio.on(SocketEvent.TYPING_START.value)
    async def handle_typing_start(sid, data):
        global user_socket_map
        cursor_position = data.get("cursorPosition", 0)
        user_socket_map = [
            ConnectedUser(
                username=u.username, roomId=u.roomId, status=u.status,
                cursorPosition=cursor_position if u.socketId == sid else u.cursorPosition,
                typing=True if u.socketId == sid else u.typing,
                socketId=u.socketId, currentFile=u.currentFile, userId=u.userId
            )
            for u in user_socket_map
        ]
        user = get_user_by_socket_id(sid)
        if user:
            await sio.emit(
                SocketEvent.TYPING_START.value,
                {"user": user_to_dict(user)},
                room=user.roomId,
                skip_sid=sid
            )

    @sio.on(SocketEvent.TYPING_PAUSE.value)
    async def handle_typing_pause(sid, data=None):
        global user_socket_map
        user_socket_map = [
            ConnectedUser(
                username=u.username, roomId=u.roomId, status=u.status,
                cursorPosition=u.cursorPosition,
                typing=False if u.socketId == sid else u.typing,
                socketId=u.socketId, currentFile=u.currentFile, userId=u.userId
            )
            for u in user_socket_map
        ]
        user = get_user_by_socket_id(sid)
        if user:
            await sio.emit(
                SocketEvent.TYPING_PAUSE.value,
                {"user": user_to_dict(user)},
                room=user.roomId,
                skip_sid=sid
            )

    # --- USER STATUS EVENTS ---

    @sio.on(SocketEvent.USER_OFFLINE.value)
    async def handle_user_offline(sid, data):
        global user_socket_map
        target_sid = data.get("socketId", sid)
        user_socket_map = [
            ConnectedUser(
                username=u.username, roomId=u.roomId,
                status=UserConnectionStatus.OFFLINE if u.socketId == target_sid else u.status,
                cursorPosition=u.cursorPosition, typing=u.typing,
                socketId=u.socketId, currentFile=u.currentFile, userId=u.userId
            )
            for u in user_socket_map
        ]
        room_id = get_room_id(target_sid)
        if room_id:
            await sio.emit(
                SocketEvent.USER_OFFLINE.value,
                {"socketId": target_sid},
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.USER_ONLINE.value)
    async def handle_user_online(sid, data):
        global user_socket_map
        target_sid = data.get("socketId", sid)
        user_socket_map = [
            ConnectedUser(
                username=u.username, roomId=u.roomId,
                status=UserConnectionStatus.ONLINE if u.socketId == target_sid else u.status,
                cursorPosition=u.cursorPosition, typing=u.typing,
                socketId=u.socketId, currentFile=u.currentFile, userId=u.userId
            )
            for u in user_socket_map
        ]
        room_id = get_room_id(target_sid)
        if room_id:
            await sio.emit(
                SocketEvent.USER_ONLINE.value,
                {"socketId": target_sid},
                room=room_id,
                skip_sid=sid
            )

    # --- WHITEBOARD EVENTS ---

    @sio.on(SocketEvent.REQUEST_DRAWING.value)
    async def handle_request_drawing(sid, data=None):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.REQUEST_DRAWING.value,
                {"socketId": sid},
                room=room_id,
                skip_sid=sid
            )

    @sio.on(SocketEvent.SYNC_DRAWING.value)
    async def handle_sync_drawing(sid, data):
        target_sid = data.get("socketId")
        if target_sid:
            await sio.emit(
                SocketEvent.SYNC_DRAWING.value,
                {"drawingData": data.get("drawingData")},
                room=target_sid
            )

    @sio.on(SocketEvent.DRAWING_UPDATE.value)
    async def handle_drawing_update(sid, data):
        room_id = get_room_id(sid)
        if room_id:
            await sio.emit(
                SocketEvent.DRAWING_UPDATE.value,
                data,
                room=room_id,
                skip_sid=sid
            )
