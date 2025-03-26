import {configureStore} from '@reduxjs/toolkit';
import loginFormReducer from './features/Auth/slices/loginFormState';
import registerFormReducer from './features/Auth/slices/registerFormState';
import tokenReducer from './features/Auth/slices/token';

const store = configureStore({
    reducer: {
        loginForm: loginFormReducer,
        registerForm: registerFormReducer,
        token: tokenReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export default store;