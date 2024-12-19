import { useState, useEffect } from 'react';

export const useDocumentSync = (documentId: string) => {
  const [content, setContent] = useState(null);
  const [version, setVersion] = useState(1);
  const [error, setError] = useState(null);

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/document/${documentId}/`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleMessage(data);
    };

    socket.onerror = (error) => {
      setError('Connection error');
    };

    return () => socket.close();
  }, [documentId]);

  const handleMessage = (message: any) => {
    switch (message.type) {
      case 'content_update':
        setContent(message.content);
        setVersion(message.version);
        break;
      case 'error':
        setError(message.error);
        break;
    }
  };

  return { content, version, error };
};
