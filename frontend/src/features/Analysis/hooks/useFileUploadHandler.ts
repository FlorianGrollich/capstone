import React, {useState, useRef, useCallback, useEffect, DragEvent, ChangeEvent} from 'react';
import {useDispatch, useSelector} from 'react-redux';
import axios, {CancelTokenSource} from 'axios';
import {AppDispatch,} from '../../../store';
import {resetUploadState, selectFileUploadState, uploadFile} from "../slices/fileUploadSlice.ts"; // Adjust paths

export interface FileUploadHookResult {
    selectedFile: File | null;
    isDraggingOver: boolean;
    uploadStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
    uploadProgress: number;
    error: string | null;
    uploadedFileUrl: string | null;
    fileInputRef: React.RefObject<HTMLInputElement>;
    handleFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
    handleDragEnter: (event: DragEvent<HTMLElement>) => void;
    handleDragLeave: (event: DragEvent<HTMLElement>) => void;
    handleDragOver: (event: DragEvent<HTMLElement>) => void;
    handleDrop: (event: DragEvent<HTMLElement>) => void;
    handleUpload: () => void;
    handleCancel: () => void;
    handleClearSelection: () => void;
}

export const useFileUploadHandler = (): FileUploadHookResult => {
    const dispatch = useDispatch<AppDispatch>();
    const {uploadStatus, uploadProgress, error, uploadedFileUrl} = useSelector(selectFileUploadState);

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isDraggingOver, setIsDraggingOver] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const cancelTokenSourceRef = useRef<CancelTokenSource | null>(null);

    const isLoading = uploadStatus === 'loading';
    const isSuccess = uploadStatus === 'succeeded';
    const isFailed = uploadStatus === 'failed';

    const reset = useCallback(() => {
        dispatch(resetUploadState());
        setSelectedFile(null);
        setIsDraggingOver(false);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
        if (cancelTokenSourceRef.current) {
            console.log("Resetting state, cancelling potential upload...");
            cancelTokenSourceRef.current.cancel('Upload cancelled due to state reset.');
            cancelTokenSourceRef.current = null;
        }
    }, [dispatch]);

    const validateAndSetFile = useCallback((file: File | null) => {
        dispatch(resetUploadState());

        if (!file) {
            setSelectedFile(null);
            return false;
        }

        if (!file.type.startsWith('video/')) {
            alert('Please select or drop a valid video file.');
            setSelectedFile(null);
            return false;
        }

        setSelectedFile(file);
        return true;
    }, [dispatch]);

    const handleFileChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0] ?? null;
        const isValid = validateAndSetFile(file);
        if (!isValid && event.target) {
            event.target.value = '';
        }
    }, [validateAndSetFile]);

    const handleDragEnter = useCallback((event: DragEvent<HTMLElement>) => {
        event.preventDefault();
        event.stopPropagation();
        if (!isLoading && !isSuccess && !isFailed) {
            setIsDraggingOver(true);
        }
    }, [isLoading, isSuccess, isFailed]);

    const handleDragLeave = useCallback((event: DragEvent<HTMLElement>) => {
        event.preventDefault();
        event.stopPropagation();
        const relatedTarget = event.relatedTarget as Node | null;
        if (!event.currentTarget.contains(relatedTarget)) {
            setIsDraggingOver(false);
        }
    }, []);

    const handleDragOver = useCallback((event: DragEvent<HTMLElement>) => {
        event.preventDefault();
        event.stopPropagation();
        if (!isLoading && !isSuccess && !isFailed) {
            setIsDraggingOver(true);
        } else {
            event.dataTransfer.dropEffect = 'none';
        }
    }, [isLoading, isSuccess, isFailed]);

    const handleDrop = useCallback((event: DragEvent<HTMLElement>) => {
        event.preventDefault();
        event.stopPropagation();
        setIsDraggingOver(false);

        if (isLoading || isSuccess || isFailed) return;

        const files = event.dataTransfer.files;
        if (files && files.length > 0) {
            validateAndSetFile(files[0]);
        } else {
            validateAndSetFile(null);
        }
    }, [isLoading, isSuccess, isFailed, validateAndSetFile]);

    const handleUpload = useCallback(() => {
        if (selectedFile && !isLoading) {
            cancelTokenSourceRef.current = axios.CancelToken.source();
            dispatch(uploadFile({
                file: selectedFile,
                cancelTokenSource: cancelTokenSourceRef.current,
            }));
        } else if (!selectedFile) {
            alert('Please select a file first.');
        }
    }, [selectedFile, isLoading, dispatch]);

    const handleCancel = useCallback(() => {
        if (cancelTokenSourceRef.current && isLoading) {
            console.log("Cancelling upload via button...");
            cancelTokenSourceRef.current.cancel('Upload cancelled by user.');
        }
    }, [isLoading]);

    const handleClearSelection = useCallback(() => {
        reset();
    }, [reset]);

    useEffect(() => {
        const currentToken = cancelTokenSourceRef.current;
        return () => {
            if (currentToken) {
                console.log('Component unmounting, cancelling potential upload...');
                currentToken.cancel('Upload cancelled due to component unmount.');
            }
        };
    }, []);


    return {
        selectedFile,
        isDraggingOver,
        uploadStatus,
        uploadProgress,
        error,
        uploadedFileUrl,
        fileInputRef,
        handleFileChange,
        handleDragEnter,
        handleDragLeave,
        handleDragOver,
        handleDrop,
        handleUpload,
        handleCancel,
        handleClearSelection,
    };
};