export interface TeamStats {
    team1: number | null;
    team2: number | null;
}

export interface StatValues {
    POSSESSION: TeamStats | null;
    PASS: TeamStats | null;
}

export interface StatsData {
    [frameCount: string]: StatValues;
}

export interface AnalysisResults {
    stats: StatsData;
}

export interface ProjectResponse {
    _id: string;
    email: string[];
    file_url: string;
    analysis_results: AnalysisResults;
    status: string;
    title: string;
}