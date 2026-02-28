from enum import Enum

class SocketEvent(Enum):
    # Connection / Room
    JOIN_REQUEST = "join_request"
    JOIN_ACCEPTED = "join_accepted"
    USER_JOINED = "user_joined"
    USER_DISCONNECTED = "user_disconnected"
    USER_OFFLINE = "user_offline"
    USER_ONLINE = "user_online"
    
    # Errors
    USERNAME_EXISTS = "username_exists"
    ERROR = "error"
    
    # File System
    SYNC_FILE_STRUCTURE = "sync_file_structure"
    FILE_CREATED = "file_created"
    FILE_UPDATED = "file_updated"
    FILE_RENAMED = "file_renamed"
    FILE_DELETED = "file_deleted"
    DIRECTORY_CREATED = "directory_created"
    DIRECTORY_UPDATED = "directory_updated" # Children update
    DIRECTORY_RENAMED = "directory_renamed"
    DIRECTORY_DELETED = "directory_deleted"
    
    # Chat
    JOIN_CHAT = "join_chat"
    LEAVE_CHAT = "leave_chat"
    SEND_MESSAGE = "send_message"
    RECEIVE_MESSAGE = "receive_message"
    
    # Whiteboard (tldraw)
    REQUEST_DRAWING = "request_drawing"
    SYNC_DRAWING = "sync_drawing"
    DRAWING_UPDATE = "drawing_update"
    
    # Cursor / Typing
    TYPING_START = "typing_start"
    TYPING_PAUSE = "typing_pause"
    CURSOR_MOVE = "cursor_move"
    
class UserConnectionStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
