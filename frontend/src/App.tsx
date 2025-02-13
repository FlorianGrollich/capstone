import * as React from "react";
import "./index.css";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import LoginPage from "./features/Auth/pages/LoginPage.tsx";
import RegistrationPage from "./features/Auth/pages/RegistrationPage.tsx";

const App: React.FC = () => {

    return (

        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginPage/>}/>
                <Route path="/registration" element={<RegistrationPage/>}/>
            </Routes>

        </BrowserRouter>);

};

export default App;
