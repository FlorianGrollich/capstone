import React, { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import videojs from "video.js";
import Player from "video.js/dist/types/player";
import "video.js/dist/video-js.css";
import { RootState, AppDispatch } from "../../store";
import { fetchProjectData, updateCurrentTime } from "./slices/analysisSlice";
import StatDualBarChart from "./components/StatDualBarChart";

const AnalysisPage: React.FC = () => {
    const videoNodeRef = useRef<HTMLVideoElement>(null);
    const playerRef = useRef<Player | null>(null);
    const dispatch = useDispatch<AppDispatch>();
    const { projectId } = useParams<{ projectId: string }>();

    const { projectData, loading, error, currentTime, currentStats } = useSelector(
        (state: RootState) => state.analysis
    );

    useEffect(() => {
        if (projectId) dispatch(fetchProjectData(projectId));
    }, [dispatch, projectId]);

    useEffect(() => {
        if (!videoNodeRef.current || !projectData?.video_url || playerRef.current) return;

        const videoElement = videoNodeRef.current;
        const videoUrl = projectData.video_url;
        const hlsSource = {
            src: videoUrl.includes("upcdn.io") ? `${videoUrl}!f=hls-h264-rt` : videoUrl,
            type: videoUrl.includes("upcdn.io") ? 'application/x-mpegURL' : 'video/mp4'
        };
        const options = {
            autoplay: false, controls: true, responsive: true, muted: true, fluid: true, sources: [hlsSource]
        };


        playerRef.current = videojs(videoElement, options, () => {
            const player = playerRef.current;
            if (!player) return;
            const handleTimeUpdate = () => {
                const time = player.currentTime();
                if(typeof time === 'number' && !isNaN(time)) dispatch(updateCurrentTime(time));
            };
            const handleError = () => console.error('Video.js Error:', player.error());
            player.on("timeupdate", handleTimeUpdate);
            player.on("seeked", handleTimeUpdate);
            player.on('error', handleError);
            player.on('dispose', () => console.log("Player disposing"));
        });

        return () => {
            const player = playerRef.current;
            if (player && !player.isDisposed()) {
                player.dispose();
                playerRef.current = null;
            }
        };
    }, [projectData?.video_url, dispatch]);


    if (loading === 'pending' || loading === 'idle') {
        return <div className="text-center py-10">Loading...</div>;
    }
    if (error) {
        return <div className="text-center py-10 text-red-500">Error: {error}</div>;
    }
    if (!projectData) {
        return <div className="text-center py-10">No project data.</div>;
    }

    const maxPossessionValue = 100;
    const maxPassesValue = 30;

    return (
        <div className="container mx-auto p-4 lg:p-6 max-w-4xl">
            <h1 className="text-2xl lg:text-3xl font-bold mb-6 text-gray-800 text-center">Video Analysis</h1>

            {/* Video Player Section */}
            <div className="video-container mb-8 shadow-lg rounded-lg overflow-hidden">
                <div data-vjs-player>
                    <video ref={videoNodeRef} className="video-js vjs-big-play-centered vjs-16-9" crossOrigin="anonymous"></video>
                </div>
            </div>

            <div className="stats-container bg-gray-50 p-4 sm:p-6 rounded-lg border border-gray-200 shadow-md">
                <h2 className="text-xl lg:text-2xl font-semibold mb-5 text-gray-700 text-center">Live Statistics</h2>

                <div className="mb-6 text-center">
                    <span className="text-sm font-medium text-gray-600">Video Time: </span>
                    <span className="text-lg font-bold text-indigo-600">{currentTime?.toFixed(2) ?? '0.00'}s</span>
                </div>

                <div className="space-y-5">
                    <StatDualBarChart
                        label="Possession"
                        team1Value={currentStats.POSSESSION?.team1}
                        team2Value={currentStats.POSSESSION?.team2}
                        maxValue={maxPossessionValue}
                        unit="%"
                    />

                    <StatDualBarChart
                        label="Passes Completed"
                        team1Value={currentStats.PASS?.team1}
                        team2Value={currentStats.PASS?.team2}
                        maxValue={maxPassesValue}
                    />
                </div>
            </div>
        </div>
    );
};

export default AnalysisPage;