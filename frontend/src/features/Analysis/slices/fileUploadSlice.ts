import {createSlice, PayloadAction} from '@reduxjs/toolkit';

interface FileUploadState {
    selectedFile: File | null;
}

const initialState: FileUploadState = {
    selectedFile: null,
};

const fileUploadSlice = createSlice({
    name: 'fileUpload',
    initialState,
    reducers: {
        setFile: (state, action: PayloadAction<File | null>) => {
            state.selectedFile = action.payload;
        },
    },
});

export const {setFile} = fileUploadSlice.actions;
export default fileUploadSlice.reducer;