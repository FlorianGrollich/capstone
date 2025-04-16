
export interface TeamStats {
    team1?: number;
    team2?: number;
}

export interface StatValues {
    POSSESSION?: TeamStats;
    PASS?: TeamStats;
    [key: string]: TeamStats | undefined;
}

export interface StatsData {
    [timestampMs: string]: StatValues;
}

export interface ProjectData {
    video_url: string;
    stats: StatsData;
}

export interface CurrentStats {
    POSSESSION: TeamStats;
    PASS: TeamStats;
}