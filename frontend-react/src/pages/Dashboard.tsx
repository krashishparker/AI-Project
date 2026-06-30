import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { resumeService } from '@/services/resume';
import { Resume } from '@/types';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Modal from '@/components/ui/Modal';
import { Upload, FileText, Trash2, MessageSquare, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import ResumeUpload from '@/components/ResumeUpload';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    loadResumes();
  }, [isAuthenticated, navigate]);

  const loadResumes = async () => {
    try {
      const data = await resumeService.getResumes();
      setResumes(data);
    } catch (error) {
      console.error('Failed to load resumes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this resume?')) return;
    
    try {
      await resumeService.deleteResume(id);
      setResumes(resumes.filter(r => r.id !== id));
    } catch (error) {
      console.error('Failed to delete resume:', error);
    }
  };

  const handleUploadSuccess = () => {
    setIsUploadModalOpen(false);
    loadResumes();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const handleChat = (resumeId: number) => {
    navigate(`/chat/${resumeId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">AI Resume Chat</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, {user?.username}</span>
            <Button variant="secondary" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">My Resumes</h2>
          <Button onClick={() => setIsUploadModalOpen(true)}>
            <Upload className="w-4 h-4 mr-2" />
            Upload Resume
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-primary-600" />
            <p className="mt-4 text-gray-600">Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <Card className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No resumes yet</h3>
            <p className="text-gray-600 mb-4">Upload your first resume to get started</p>
            <Button onClick={() => setIsUploadModalOpen(true)}>
              <Upload className="w-4 h-4 mr-2" />
              Upload Resume
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {resumes.map((resume) => (
              <Card key={resume.id} className="hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary-600" />
                    <h3 className="font-medium text-gray-900 truncate">
                      {resume.filename}
                    </h3>
                  </div>
                  {getStatusIcon(resume.processing_status)}
                </div>

                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <p>
                    <span className="font-medium">Size:</span>{' '}
                    {(resume.file_size / 1024).toFixed(2)} KB
                  </p>
                  <p>
                    <span className="font-medium">Type:</span>{' '}
                    {resume.file_type}
                  </p>
                  <p>
                    <span className="font-medium">Uploaded:</span>{' '}
                    {new Date(resume.created_at).toLocaleDateString()}
                  </p>
                </div>

                {resume.error_message && (
                  <div className="bg-red-50 text-red-600 p-2 rounded text-sm mb-4">
                    {resume.error_message}
                  </div>
                )}

                <div className="flex gap-2">
                  {resume.processing_status === 'completed' && (
                    <Button
                      variant="primary"
                      className="flex-1"
                      onClick={() => handleChat(resume.id)}
                    >
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Chat
                    </Button>
                  )}
                  <Button
                    variant="danger"
                    onClick={() => handleDelete(resume.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>

      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Resume"
      >
        <ResumeUpload onSuccess={handleUploadSuccess} />
      </Modal>
    </div>
  );
}
