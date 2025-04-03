import React, {ChangeEvent, DragEvent} from 'react';
import Button from '../../components/Button'; // Adjust path
import {FiUploadCloud, FiCheckCircle, FiAlertCircle, FiX, FiLoader, FiVideo} from 'react-icons/fi';

// Define the props the view component expects
interface FileUploadViewProps {
    selectedFile: File | null;
    isDraggingOver: boolean;
    uploadStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
    uploadProgress: number;
    error: string | null;
    uploadedFileUrl: string | null;
    fileInputRef: React.RefObject<HTMLInputElement>;
    onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
    onDragEnter: (event: DragEvent<HTMLLabelElement>) => void; // Specific to label
    onDragLeave: (event: DragEvent<HTMLLabelElement>) => void;
    onDragOver: (event: DragEvent<HTMLLabelElement>) => void;
    onDrop: (event: DragEvent<HTMLLabelElement>) => void;
    onUploadClick: () => void;
    onCancelClick: () => void;
    onClearSelectionClick: () => void;
}

export const FileUploadView: React.FC<FileUploadViewProps> = ({
                                                                  selectedFile,
                                                                  isDraggingOver,
                                                                  uploadStatus,
                                                                  uploadProgress,
                                                                  error,
                                                                  uploadedFileUrl,
                                                                  fileInputRef,
                                                                  onFileChange,
                                                                  onDragEnter,
                                                                  onDragLeave,
                                                                  onDragOver,
                                                                  onDrop,
                                                                  onUploadClick,
                                                                  onCancelClick,
                                                                  onClearSelectionClick,
                                                              }) => {

    const isLoading = uploadStatus === 'loading';
    const isSuccess = uploadStatus === 'succeeded';
    const isFailed = uploadStatus === 'failed';

    // --- Render Logic (Copied and adapted from previous version) ---
    const renderDropzoneContent = () => {
        // ... (Keep the exact same rendering logic from the previous good version)
        // Replace state variable checks (e.g., `isLoading`) with prop checks
        // Replace handler calls (e.g., `handleClearSelection`) with prop calls (e.g., `onClearSelectionClick`)

        if (isLoading) {
            return (
                <div className="text-center text-gray-600">
                    <FiLoader className="animate-spin h-10 w-10 mx-auto mb-3 text-primary"/>
                    <p className="font-semibold">Uploading {selectedFile?.name ?? 'file'}...</p>
                    <p className="text-sm">{uploadProgress}% Complete</p>
                </div>
            );
        }

        if (isSuccess) {
            return (
                <div className="text-center text-primary">
                    <FiCheckCircle className="h-10 w-10 mx-auto mb-3"/>
                    <p className="font-semibold">Upload Successful!</p>
                    {uploadedFileUrl && (
                        <p className="text-sm mt-1">
                            URL: <a href={uploadedFileUrl} target="_blank" rel="noopener noreferrer"
                                    className="underline hover:text-primary-dark">{uploadedFileUrl}</a>
                        </p>
                    )}
                    <p className="text-sm text-gray-500 mt-3">Select or drag another video to upload.</p>
                </div>
            );
        }

        if (isFailed) {
            return (
                <div className="text-center text-red-600">
                    <FiAlertCircle className="h-10 w-10 mx-auto mb-3"/>
                    <p className="font-semibold">Upload Failed</p>
                    <p className="text-sm mt-1 max-w-xs mx-auto">{error || 'An unknown error occurred.'}</p>
                    <p className="text-sm text-gray-500 mt-3">Please try again or select a different file.</p>
                </div>
            );
        }

        if (selectedFile) {
            return (
                <div className="text-center text-gray-700 relative group">
                    <button
                        onClick={onClearSelectionClick} // Use prop handler
                        className="absolute -top-2 -right-2 p-1.5 bg-white rounded-full text-gray-400 hover:text-red-500 focus:outline-none focus:ring-2 focus:ring-red-400 opacity-0 group-hover:opacity-100 transition-opacity z-10"
                        aria-label="Clear selection"
                    >
                        <FiX size={18}/>
                    </button>
                    <FiVideo className="h-10 w-10 mx-auto mb-3 text-primary"/>
                    <p className="font-semibold">File Ready:</p>
                    <p className="text-sm mt-1 truncate px-4" title={selectedFile.name}>{selectedFile.name}</p>
                    <p className="text-xs text-gray-500 mt-1">({(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)</p>
                </div>
            );
        }

        // Default / Idle state / Dragging Over state
        const idleText = isDraggingOver ? "Drop the video file here!" : "Click or drag video file here";
        const idleIconColor = isDraggingOver ? "text-primary" : "text-gray-400";

        return (
            <div className={`text-center ${isDraggingOver ? 'text-primary' : 'text-gray-500'}`}>
                <FiUploadCloud className={`h-12 w-12 mx-auto mb-3 ${idleIconColor} transition-colors`}/>
                <p className="font-semibold">{idleText}</p>
                {!isDraggingOver && <p className="text-sm">Supports standard video formats</p>}
                {!isDraggingOver && <p className="text-xs mt-2">(Max size: e.g., 100MB)</p>}
            </div>
        );

    };

    // Define base classes for the dropzone label - strictly light theme
    const dropzoneBaseClasses = `
        relative flex flex-col items-center justify-center w-full h-64 px-4
        border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-200 ease-in-out
        bg-white
    `;

    // Define state-specific classes - strictly light theme
    const getDropzoneStateClasses = () => {
        if (isDraggingOver) return 'border-primary bg-green-50 scale-105'; // Highlight border, light green bg, slight scale up
        if (isLoading) return 'border-gray-300 opacity-70';
        if (isSuccess) return 'border-primary bg-green-50'; // Use primary border, light green bg
        if (isFailed) return 'border-red-400 bg-red-50'; // Use red border, light red bg
        // Idle state with primary hover
        return 'border-gray-300 hover:border-primary';
    };


    return (
        <div className="w-full max-w-xl">
            <label
                htmlFor="file-upload"
                className={`${dropzoneBaseClasses} ${getDropzoneStateClasses()}`}
                // Add Drag and Drop Handlers from props
                onDragEnter={onDragEnter}
                onDragLeave={onDragLeave}
                onDragOver={onDragOver}
                onDrop={onDrop}
                aria-busy={isLoading}
                aria-invalid={isFailed}
            >
                {renderDropzoneContent()}
                <input
                    ref={fileInputRef} // Pass ref from props
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    accept="video/*"
                    onChange={onFileChange} // Use prop handler
                    disabled={isLoading}
                    className="sr-only"
                />
            </label>

            {/* Progress Bar */}
            {isLoading && (
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-5 overflow-hidden">
                    <div
                        className="bg-primary h-2.5 rounded-full transition-all duration-300 ease-out"
                        style={{width: `${uploadProgress}%`}}
                    ></div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex justify-center items-center space-x-4 mt-6 min-h-[50px]">
                {!isLoading && !isSuccess && !isFailed && selectedFile && (
                    <Button
                        onClick={onUploadClick} // Use prop handler
                        disabled={isLoading}
                    >
                        <FiUploadCloud className="mr-2 h-5 w-5"/>
                        Upload File
                    </Button>
                )}
                {isLoading && (
                    <Button
                        onClick={onCancelClick} // Use prop handler
                        className="bg-red-600 hover:bg-red-700 text-white"
                    >
                        <FiX className="mr-2 h-5 w-5"/>
                        Cancel Upload
                    </Button>
                )}
            </div>
        </div>
    );
};