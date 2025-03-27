import * as React from "react";
import "./index.css";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import LoginPage from "./features/Auth/pages/LoginPage.tsx";
import RegistrationPage from "./features/Auth/pages/RegistrationPage.tsx";
import ProjectMenu from "./features/Project/pages/ProjectMenu.tsx";
import Layout from "./components/Layout.tsx";
import {Provider} from "react-redux";
import store from "./store.ts";
import AnalysisPage from "./features/Analysis/AnalysisPage.tsx";

const App: React.FC = () => {

    return (
        <Provider store={store}>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/register" element={<RegistrationPage/>}/>
                    <Route element={<Layout/>}>
                        <Route path="/" element={<ProjectMenu/>}/>
                        <Route path="/analysis" element={<AnalysisPage/>}/>
                        <Route path="/project" element={<ProjectMenu/>}/>
                    </Route>
                </Routes>
            </BrowserRouter>
        </Provider>);
};

export default App;
