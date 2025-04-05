import React, { useEffect, useState, useRef } from 'react';
import { Project } from '../slices/projectSlice';
import { FiLoader, FiAlertCircle, FiVideo } from 'react-icons/fi';

interface ProjectTileProps {
  project: Project;
}

const ProjectTile: React.FC<ProjectTileProps> = ({ project }) => {
  const [thumbnail, setThumbnail] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (project.video_url && project.state === 'finished') {
      const video = videoRef.current;
      if (video) {
        video.onloadeddata = () => {
          video.currentTime = 0;
        };

        video.onseeked = () => {
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const dataUrl = canvas.toDataURL('image/jpeg');
            setThumbnail(dataUrl);
          }
        };

        video.src = project.video_url;
        video.load();
      }
    }
  }, [project.video_url, project.state]);

  const renderContent = () => {
    switch (project.state) {
      case 'loading':
        return (
          <div className="flex flex-col items-center justify-center h-full">
            <FiLoader className="animate-spin h-10 w-10 text-primary mb-3" />
            <p className="font-semibold text-gray-600">Processing...</p>
          </div>
        );
      case 'error':
        return (
          <div className="flex flex-col items-center justify-center h-full">
            <FiAlertCircle className="h-10 w-10 text-red-500 mb-3" />
            <p className="font-semibold text-red-600">Error</p>
          </div>
        );
      case 'finished':
        return thumbnail ? (
          <img
            src={thumbnail}
            alt={project.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full">
            <FiVideo className="h-10 w-10 text-primary mb-3" />
            <p className="font-semibold text-gray-600">Loading thumbnail...</p>
          </div>
        );
    }
  };

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div className="aspect-video bg-gray-100 relative">
        {renderContent()}
        <video ref={videoRef} className="hidden" />
      </div>
      <div className="p-3">
        <h3 className="font-medium text-gray-800">{project.title}</h3>
        <p className="text-sm text-gray-500 capitalize mt-1">{project.state}</p>
      </div>
    </div>
  );
};

export default ProjectTile;