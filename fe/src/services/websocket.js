import { io } from 'socket.io-client';
import Cookies from 'js-cookie';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
    this.eventListeners = new Map();
  }

  connect(userId) {
    if (this.socket) {
      console.log('[WebSocket] Disconnecting existing socket');
      this.disconnect();
    }

    const token = Cookies.get('access_token');
    
    const wsUrl = process.env.REACT_APP_WS_URL || 'http://localhost:8001';
    
    console.log('[WebSocket] Connecting to:', wsUrl);
    console.log('[WebSocket] User ID:', userId);
    console.log('[WebSocket] Token present:', !!token);
    
    this.socket = io(wsUrl, {
      auth: {
        user_id: userId,
        token: token || ''
      },
      transports: ['polling', 'websocket'],  // Try polling first, then upgrade to websocket
      upgrade: true,
      rememberUpgrade: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      timeout: 20000,
      autoConnect: true
    });

    this.setupEventHandlers();
  }

  setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('[WebSocket] ✓ Connected successfully');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected. Reason:', reason);
      this.isConnected = false;
      this.emit('connection_status', { connected: false, reason });
      
      if (reason === 'io server disconnect') {
        // Server disconnected, need manual reconnection
        console.log('[WebSocket] Server initiated disconnect, scheduling reconnect');
        this.scheduleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error);
      console.error('[WebSocket] Error details:', {
        message: error.message,
        description: error.description,
        context: error.context,
        type: error.type
      });
      this.emit('connection_error', { error });
      this.scheduleReconnect();
    });

    this.socket.on('connection_status', (data) => {
      this.emit('connection_status', data);
    });

    this.socket.on('message', (data) => {
      this.handleMessage(data);
    });

    this.socket.on('broadcast', (data) => {
      this.emit('broadcast', data);
    });

    this.socket.on('room_joined', (data) => {
      this.emit('room_joined', data);
    });

    this.socket.on('room_left', (data) => {
      this.emit('room_left', data);
    });

    this.socket.on('pong', (data) => {
      this.emit('pong', data);
    });

    // Enhanced chat events
    this.socket.on('chat_response', (data) => {
      this.emit('chat_response', data);
    });

    this.socket.on('typing', (data) => {
      this.emit('typing', data);
    });

    this.socket.on('session_joined', (data) => {
      this.emit('session_joined', data);
    });

    this.socket.on('session_left', (data) => {
      this.emit('session_left', data);
    });

    this.socket.on('chat_history', (data) => {
      this.emit('chat_history', data);
    });

    this.socket.on('error', (data) => {
      this.emit('error', data);
    });

    // Direct event handlers for file upload events (backend emits these directly)
    this.socket.on('file_upload_progress', (data) => {
      this.emit('file_upload_progress', data);
    });

    this.socket.on('file_upload_complete', (data) => {
      this.emit('file_upload_complete', data);
    });

    this.socket.on('file_upload_error', (data) => {
      this.emit('file_upload_error', data);
    });

    this.socket.on('file_processing_update', (data) => {
      this.emit('file_processing_update', data);
    });

    this.socket.on('bulk_upload_progress', (data) => {
      this.emit('bulk_upload_progress', data);
    });

    this.socket.on('bulk_upload_complete', (data) => {
      this.emit('bulk_upload_complete', data);
    });

    this.socket.on('bulk_upload_error', (data) => {
      this.emit('bulk_upload_error', data);
    });
  }

  handleMessage(data) {
    const { type } = data;
    
    switch (type) {
      case 'file_upload_progress':
        this.emit('file_upload_progress', data);
        break;
      case 'file_upload_complete':
        this.emit('file_upload_complete', data);
        break;
      case 'file_upload_error':
        this.emit('file_upload_error', data);
        break;
      case 'bulk_upload_progress':
        this.emit('bulk_upload_progress', data);
        break;
      case 'bulk_upload_complete':
        this.emit('bulk_upload_complete', data);
        break;
      case 'bulk_upload_error':
        this.emit('bulk_upload_error', data);
        break;
      default:
        this.emit('message', data);
        break;
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.emit('max_reconnect_attempts_reached');
      return;
    }

    this.reconnectAttempts++;
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.socket?.connect();
      }
    }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)); // Exponential backoff
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinRoom(room) {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_room', { room });
    }
  }

  leaveRoom(room) {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_room', { room });
    }
  }

  ping(timestamp = Date.now()) {
    if (this.socket && this.isConnected) {
      this.socket.emit('ping', { timestamp });
    }
  }

  // Event listener management
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event);
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          // Silently handle event listener errors to avoid console spam
        }
      });
    }
  }

  // Utility methods
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts
    };
  }

  isSocketConnected() {
    return this.socket && this.isConnected;
  }

  // Enhanced chat methods
  sendChatMessage(message, sessionId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('chat_message', {
        message: message,
        session_id: sessionId
      });
    }
  }

  joinChatSession(sessionId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_chat_session', {
        session_id: sessionId
      });
    }
  }

  leaveChatSession(sessionId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_chat_session', {
        session_id: sessionId
      });
    }
  }

  getChatHistory(sessionId, limit = 20) {
    if (this.socket && this.isConnected) {
      this.socket.emit('get_chat_history', {
        session_id: sessionId,
        limit: limit
      });
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
