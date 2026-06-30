import { useState } from 'react';
import { resumeService } from '@/services/resume';
import Input from '@/components/ui/Input';
import Button from '@/components/ui/Button';
import { Upload, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react';

interface ResumeUploadProps {
  onSuccess: () => void;
}

export default function ResumeUpload({ onSuccess }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Only PDF and DOCX files are allowed');
        setFile(null);
        return;
      }

      // Validate file size (10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        setFile(null);
        return;
      }

      setFile(selectedFile);
      setError('');
      setUploadStatus('idle');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError('');

    try {
      await resumeService.uploadResume(file);
      setUploadStatus('success');
      setTimeout(() => {
        onSuccess();
      }, 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
        <input
          type="file"
          id="resume-upload"
          className="hidden"
          accept=".pdf,.docx"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <label
          htmlFor="resume-upload"
          className="cursor-pointer flex flex-col items-center"
        >
          {file ? (
            <>
              <FileText className="w-12 h-12 text-primary-600 mb-2" />
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-600">
                {(file.size / 1024).toFixed(2)} KB
              </p>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400 mb-2" />
              <p className="text-gray-600">
                Click to upload or drag and drop
              </p>
              <p className="text-sm text-gray-500 mt-1">
                PDF or DOCX (max 10MB)
              </p>
            </>
          )}
        </label>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm flex items-center gap-2">
          <XCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="bg-green-50 text-green-600 p-3 rounded-lg text-sm flex items-center gap-2">
          <CheckCircle className="w-4 h-4" />
          Resume uploaded successfully! Processing...
        </div>
      )}

      <div className="flex gap-2">
        <Button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="flex-1"
          isLoading={isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Resume'}
        </Button>
        <Button
          variant="secondary"
          onClick={() => setFile(null)}
          disabled={isUploading}
        >
          Clear
        </Button>
      </div>
    </div>
  );
}
