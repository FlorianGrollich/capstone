import * as React from "react";
import "./index.css";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import LoginPage from "./features/Auth/pages/LoginPage.tsx";
import RegistrationPage from "./features/Auth/pages/RegistrationPage.tsx";
import ProjectMenu from "./features/Project/pages/ProjectMenu.tsx";
import Layout from "./components/Layout.tsx";

const App: React.FC = () => {

    return (

        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage/>} />
                <Route path="/register" element={<RegistrationPage/>} />
                <Route element={<Layout/>}>
                    <Route path="/" element={<ProjectMenu/>}/>
                    <Route path="/project" element={<ProjectMenu/>}/>
                </Route>
            </Routes>

        </BrowserRouter>);

};

export default App;
