import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
}

export class ChatErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ChatWidget error:', error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-lg shadow-xl flex flex-col items-center justify-center z-50 p-6 text-center">
          <AlertTriangle className="h-12 w-12 text-yellow-500 mb-4" />
          <p className="font-medium text-gray-800 mb-2">
            Le chat a rencontr&eacute; un probl&egrave;me.
          </p>
          <p className="text-sm text-gray-500 mb-4">
            Une erreur inattendue s'est produite.
          </p>
          <button
            onClick={this.handleRetry}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            R&eacute;essayer
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ChatErrorBoundary;
