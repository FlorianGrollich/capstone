import React from 'react';

interface StatDualBarChartProps {
    label: string;
    team1Value: number | null | undefined;
    team2Value: number | null | undefined;
    maxValue: number;
    unit?: string;
    team1Color?: string;
    team2Color?: string;
}

const StatDualBarChart: React.FC<StatDualBarChartProps> = ({
                                                               label,
                                                               team1Value,
                                                               team2Value,
                                                               maxValue,
                                                               unit = "",
                                                               team1Color = "bg-blue-600",
                                                               team2Color = "bg-red-600"
                                                           }) => {

    // Handle null or undefined values
    const validTeam1Value = team1Value !== null && team1Value !== undefined ? team1Value : 0;
    const validTeam2Value = team2Value !== null && team2Value !== undefined ? team2Value : 0;

    // Calculate percentage width relative to the maxValue for each half
    const calculateWidthPercentage = (value: number): string => {
        if (maxValue <= 0) return '0%';
        const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
        return `${percentage}%`;
    };

    const team1Width = calculateWidthPercentage(validTeam1Value);
    const team2Width = calculateWidthPercentage(validTeam2Value);

    const formatValue = (value: number | null | undefined): string => {
        if (value === null || value === undefined) return '-';
        return `${value.toFixed(0)}${unit}`;
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">{label}</h3>

            <div className="flex items-center w-full space-x-2 sm:space-x-3">
                {/* Team 1 Value (Left) */}
                <span className={`w-12 sm:w-16 text-right text-sm font-bold ${team1Color.replace('bg-', 'text-')}`}>
                    {formatValue(team1Value)}
                </span>

                {/* Central Bar Area */}
                <div className="flex-1 flex items-center h-5 bg-gray-200 rounded-full overflow-hidden">
                    {/* Team 1 Bar (Grows Left from Center) */}
                    <div className="flex-1 flex justify-end h-full" title={`Team 1 ${label}: ${formatValue(team1Value)}`}>
                        <div
                            className={`${team1Color} h-full rounded-l-full transition-all duration-300 ease-in-out`}
                            style={{ width: team1Width }}
                        ></div>
                    </div>

                    {/* Team 2 Bar (Grows Right from Center) */}
                    <div className="flex-1 flex justify-start h-full" title={`Team 2 ${label}: ${formatValue(team2Value)}`}>
                        <div
                            className={`${team2Color} h-full rounded-r-full transition-all duration-300 ease-in-out`}
                            style={{ width: team2Width }}
                        ></div>
                    </div>
                </div>

                {/* Team 2 Value (Right) */}
                <span className={`w-12 sm:w-16 text-left text-sm font-bold ${team2Color.replace('bg-', 'text-')}`}>
                    {formatValue(team2Value)}
                </span>
            </div>
        </div>
    );
};

export default StatDualBarChart;