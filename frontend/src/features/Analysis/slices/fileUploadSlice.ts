import {createSlice, PayloadAction} from "@reduxjs/toolkit";


import {createAsyncThunk} from '@reduxjs/toolkit';
import axios from 'axios';

export const uploadFile = createAsyncThunk(
    'fileUpload/uploadFile',
    async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        console.log("upoad file");

        const response = await axios.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    }
);


interface FileUploadState {
    selectedFile: File | null;
    uploadProgress: number;
}

const initialState: FileUploadState = {
    selectedFile: null,
    uploadProgress: 0,
};

const fileUploadSlice = createSlice({
    name: 'fileUpload',
    initialState,
    reducers: {
        setFile: (state, action: PayloadAction<File | null>) => {
            state.selectedFile = action.payload;
        }
    },
    extraReducers: (builder) => {
        builder.addCase(uploadFile.fulfilled, (state) => {
            state.uploadProgress = 100;
        });
    },
});


export const selectFile = (state: FileUploadState) => state.selectedFile;


export const {setFile} = fileUploadSlice.actions;
export default fileUploadSlice.reducer;