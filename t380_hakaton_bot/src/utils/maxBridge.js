class MaxBridge {
  constructor() {
    this.isAvailable = typeof window !== 'undefined' && window.maxBridge;
    this.bridge = this.isAvailable ? window.maxBridge : null;
  }

  async getUserId() {
    if (!this.isAvailable) {
      return 'local';
    }

    try {
      if (this.bridge.getUserInfo) {
        const userInfo = await this.bridge.getUserInfo();
        return userInfo?.userId || 'local';
      }
      return 'local';
    } catch (error) {
      console.error('MAX Bridge getUserInfo error:', error);
      return 'local';
    }
  }

  async get(key) {
    const userId = await this.getUserId();
    const storageKey = `${userId}_${key}`;

    if (!this.isAvailable) {
      const value = localStorage.getItem(storageKey);
      return value ? JSON.parse(value) : null;
    }

    try {
      if (this.bridge.get) {
        const result = await this.bridge.get(key);
        return result?.value ? JSON.parse(result.value) : result ? JSON.parse(result) : null;
      }
      const value = localStorage.getItem(storageKey);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('MAX Bridge get error:', error);
      const value = localStorage.getItem(storageKey);
      return value ? JSON.parse(value) : null;
    }
  }

  async set(key, value) {
    const userId = await this.getUserId();
    const storageKey = `${userId}_${key}`;
    const stringValue = JSON.stringify(value);
    
    if (!this.isAvailable) {
      localStorage.setItem(storageKey, stringValue);
      return;
    }

    try {
      if (this.bridge.set) {
        await this.bridge.set(key, stringValue);
      }
      localStorage.setItem(storageKey, stringValue);
    } catch (error) {
      console.error('MAX Bridge set error:', error);
      localStorage.setItem(storageKey, stringValue);
    }
  }

  async remove(key) {
    const userId = await this.getUserId();
    const storageKey = `${userId}_${key}`;

    if (!this.isAvailable) {
      localStorage.removeItem(storageKey);
      return;
    }

    try {
      if (this.bridge.remove) {
        await this.bridge.remove(key);
      }
      localStorage.removeItem(storageKey);
    } catch (error) {
      console.error('MAX Bridge remove error:', error);
      localStorage.removeItem(storageKey);
    }
  }
}

export const maxBridge = new MaxBridge();

