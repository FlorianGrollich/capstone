import {createSlice, createAsyncThunk, PayloadAction} from '@reduxjs/toolkit';
import {AxiosProgressEvent, CancelTokenSource, isCancel, isAxiosError} from 'axios';
import {RootState} from '../../../store.ts';
import axiosClient from "../../../api/axiosClient.ts";


interface UploadResponse {
    message: string;
    fileUrl?: string;
}

interface UploadFilePayload {
    file: File;
    cancelTokenSource?: CancelTokenSource;
}

interface FileUploadState {
    uploadStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
    uploadProgress: number;
    error: string | null;
    uploadedFileUrl: string | null;
}

const initialState: FileUploadState = {
    uploadStatus: 'idle',
    uploadProgress: 0,
    error: null,
    uploadedFileUrl: null,
};

const setUploadProgress = (state: FileUploadState, action: PayloadAction<number>) => {
    state.uploadProgress = action.payload;
};

export const uploadFile = createAsyncThunk<
    UploadResponse,
    UploadFilePayload,
    {
        state: RootState;
        rejectValue: string;
    }
>(
    'fileUpload/uploadFile',
    async ({file, cancelTokenSource}, thunkAPI) => {
        const formData = new FormData();
        formData.append('file', file, file.name);

        console.log("Starting upload for:", file.name);

        thunkAPI.dispatch(fileUploadSlice.actions.setUploadProgress(0));

        try {
            const response = await axiosClient.post<UploadResponse>(
                '/upload',
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
                        if (progressEvent.total) {
                            const percentCompleted = Math.round(
                                (progressEvent.loaded * 100) / progressEvent.total
                            );
                            thunkAPI.dispatch(fileUploadSlice.actions.setUploadProgress(percentCompleted));
                            console.log(`Upload Progress: ${percentCompleted}%`);
                        }
                    },
                    cancelToken: cancelTokenSource?.token,
                }
            );

            console.log('Upload successful:', response.data);
            return response.data;

        } catch (error: unknown) {
            let errorMessage = 'File upload failed.';

            if (isCancel(error)) {
                errorMessage = 'Upload cancelled.';
                console.log('Request canceled:', (error as { message: string }).message);
            } else if (isAxiosError(error)) {
                console.error('Axios Error Code:', error.code); // e.g. 'ERR_NETWORK'
                if (error.response) {
                    console.error('Server Error Status:', error.response.status);
                    console.error('Server Error Data:', error.response.data);
                    const serverMessage = (error.response.data as { message?: string })?.message;
                    errorMessage = serverMessage || `Server error: ${error.response.status}`;
                } else if (error.request) {
                    console.error('Network Error:', error.request);
                    errorMessage = 'Network error. Please check connection.';
                } else {
                    console.error('Axios Setup Error:', error.message);
                    errorMessage = error.message || 'Error setting up upload request.';
                }
            } else if (error instanceof Error) {
                console.error('Generic Error:', error.message);
                errorMessage = error.message;
            } else {
                console.error('Unknown Error Type:', error);
                errorMessage = 'An unexpected error occurred.';
            }

            return thunkAPI.rejectWithValue(errorMessage);
        }
    }
);

const fileUploadSlice = createSlice({
    name: 'fileUpload',
    initialState,
    reducers: {
        setUploadProgress,
        resetUploadState: (state) => {
            state.uploadStatus = 'idle';
            state.uploadProgress = 0;
            state.error = null;
            state.uploadedFileUrl = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(uploadFile.pending, (state) => {
                state.uploadStatus = 'loading';
                state.error = null;
                state.uploadedFileUrl = null;
            })
            .addCase(uploadFile.fulfilled, (state, action: PayloadAction<UploadResponse>) => {
                state.uploadStatus = 'succeeded';
                state.uploadProgress = 100;
                state.uploadedFileUrl = action.payload.fileUrl ?? null;
                state.error = null;
            })
            .addCase(uploadFile.rejected, (state, action) => {
                state.uploadStatus = 'failed';
                state.error = typeof action.payload === 'string' ? action.payload : (action.error.message ?? 'Upload failed');
            });
    },
});

export const selectFileUploadState = (state: RootState) => state.fileUpload;

export const {resetUploadState} = fileUploadSlice.actions;

export default fileUploadSlice.reducer;