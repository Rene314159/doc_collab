import React, { useEffect, useState, useCallback } from 'react';
import { Editor } from 'slate-react';
import { createEditor, Node } from 'slate';
import debounce from 'lodash/debounce';

interface DocumentEditorProps {
  documentId: string;
}

const DocumentEditor: React.FC<DocumentEditorProps> = ({ documentId }) => {
  const [editor] = useState(() => createEditor());
  const [content, setContent] = useState<Node[]>([]);
  const [version, setVersion] = useState(1);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/document/${documentId}/`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'operation') {
        applyOperation(data.operation);
        setVersion(data.operation.version);
      } else if (data.type === 'document_state') {
        setContent(data.content);
        setVersion(data.version);
        setLoading(false);
      }
    };

    setSocket(ws);
    return () => ws.close();
  }, [documentId]);

  const sendOperation = useCallback(
    debounce((operation: any) => {
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
          type: operation.type,
          data: operation.data,
          version: version
        }));
      }
    }, 100),
    [socket, version]
  );

  const handleChange = (newContent: Node[]) => {
    const operations = editor.operations
      .filter(op => op.type !== 'set_selection')
      .map(op => ({
        type: op.type,
        data: op
      }));

    operations.forEach(sendOperation);
    setContent(newContent);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="document-editor">
      <Editor
        editor={editor}
        value={content}
        onChange={handleChange}
      />
    </div>
  );
};

export default DocumentEditor;
