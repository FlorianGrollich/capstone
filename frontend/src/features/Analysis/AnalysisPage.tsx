import React from "react";


const AnalysisPage: React.FC = () => {
    return (
        <div><video controls width="300" height="300">
                <source type="video/mp4" src="/output.mp4" />
            </video>
        </div>
    );
};

export default AnalysisPage;