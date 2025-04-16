import {configureStore} from '@reduxjs/toolkit';
import loginFormReducer from './features/Auth/slices/loginFormState';
import registerFormReducer from './features/Auth/slices/registerFormState';
import authReducer from './features/Auth/slices/authState';
import fileUploadReducer from './features/Analysis/slices/fileUploadSlice';
import projectReducer from './features/Project/slices/projectSlice';
import analysisReducer from './features/Analysis/slices/analysisSlice';


const store = configureStore({
    reducer: {
        loginForm: loginFormReducer,
        registerForm: registerFormReducer,
        fileUpload: fileUploadReducer,
        authState: authReducer,
        project: projectReducer,
        analysis: analysisReducer
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: {
                ignoredActions: ['fileUpload/setFile'],
                ignoredPaths: ['fileUpload.selectedFile'],
            },
        }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export default store;