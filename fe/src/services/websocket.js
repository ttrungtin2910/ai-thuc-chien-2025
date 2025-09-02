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
      this.disconnect();
    }

    const token = Cookies.get('access_token');
    
    this.socket = io('http://localhost:8001', {
      auth: {
        user_id: userId,
        token: token
      },
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true
    });

    this.setupEventHandlers();
  }

  setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connection_status', { connected: true });
    });

    this.socket.on('disconnect', (reason) => {
      this.isConnected = false;
      this.emit('connection_status', { connected: false, reason });
      
      if (reason === 'io server disconnect') {
        // Server disconnected, need manual reconnection
        this.scheduleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
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
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
