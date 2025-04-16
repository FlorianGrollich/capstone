import React from 'react';
import {useFileUploadHandler} from '../hooks/useFileUploadHandler.ts';
import {FileUploadView} from '../components/FileUploadView.tsx';

const FileUploadPage: React.FC = () => {
    const fileUploadProps = useFileUploadHandler();

    return (
        <div className="p-6 md:p-10 min-h-screen flex flex-col items-center bg-white">
            <h1 className="text-3xl font-bold mb-8 ">Upload Your Video</h1>

            <FileUploadView
                selectedFile={fileUploadProps.selectedFile}
                isDraggingOver={fileUploadProps.isDraggingOver}
                uploadStatus={fileUploadProps.uploadStatus}
                uploadProgress={fileUploadProps.uploadProgress}
                error={fileUploadProps.error}
                uploadedFileUrl={fileUploadProps.uploadedFileUrl}
                fileInputRef={fileUploadProps.fileInputRef}
                onFileChange={fileUploadProps.handleFileChange}
                onDragEnter={fileUploadProps.handleDragEnter}
                onDragLeave={fileUploadProps.handleDragLeave}
                onDragOver={fileUploadProps.handleDragOver}
                onDrop={fileUploadProps.handleDrop}
                onUploadClick={fileUploadProps.handleUpload}
                onCancelClick={fileUploadProps.handleCancel}
                onClearSelectionClick={fileUploadProps.handleClearSelection}
            />
        </div>
    );
};

export default FileUploadPage;