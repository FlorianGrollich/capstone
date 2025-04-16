// src/features/analysis/components/StatDualBarChart.tsx (Create this new file)

import React from 'react';

interface StatDualBarChartProps {
    label: string;
    team1Value?: number;
    team2Value?: number;
    maxValue: number; // The maximum value each bar can represent (determines 100% width within its half)
    unit?: string;
    team1Color?: string;
    team2Color?: string;
}

const StatDualBarChart: React.FC<StatDualBarChartProps> = ({
                                                               label,
                                                               team1Value = 0,
                                                               team2Value = 0,
                                                               maxValue,
                                                               unit = "",
                                                               team1Color = "bg-blue-600",
                                                               team2Color = "bg-red-600"
                                                           }) => {

    // Ensure values are non-negative
    const validTeam1Value = Math.max(0, team1Value);
    const validTeam2Value = Math.max(0, team2Value);

    // Calculate percentage width relative to the maxValue for each half
    // A value equal to maxValue means the bar fills its entire half (100% width of that half)
    const calculateWidthPercentage = (value: number): string => {
        if (maxValue <= 0) return '0%';
        const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
        return `${percentage}%`;
    };

    const team1Width = calculateWidthPercentage(validTeam1Value);
    const team2Width = calculateWidthPercentage(validTeam2Value);

    const formatValue = (value: number): string => {
        // Adjust formatting if needed (e.g., for percentages vs counts)
        return `${value.toFixed(0)}${unit}`;
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-700 mb-4 text-center">{label}</h3>

            <div className="flex items-center w-full space-x-2 sm:space-x-3">

                {/* Team 1 Value (Left) */}
                <span className={`w-12 sm:w-16 text-right text-sm font-bold ${team1Color.replace('bg-', 'text-')}`}>
                    {formatValue(validTeam1Value)}
                </span>

                {/* Central Bar Area */}
                <div className="flex-1 flex items-center h-5 bg-gray-200 rounded-full overflow-hidden"> {/* Bar track */}

                    {/* Team 1 Bar (Grows Left from Center) */}
                    {/* Container fills left half, aligns colored bar to its right edge */}
                    <div className="flex-1 flex justify-end h-full" title={`Team 1 ${label}: ${formatValue(validTeam1Value)}`}>
                        <div
                            className={`${team1Color} h-full rounded-l-full transition-all duration-300 ease-in-out`}
                            style={{ width: team1Width }} // Width relative to its container (flex-1)
                        ></div>
                    </div>

                    {/* Team 2 Bar (Grows Right from Center) */}
                    {/* Container fills right half, aligns colored bar to its left edge */}
                    <div className="flex-1 flex justify-start h-full" title={`Team 2 ${label}: ${formatValue(validTeam2Value)}`}>
                        <div
                            className={`${team2Color} h-full rounded-r-full transition-all duration-300 ease-in-out`}
                            style={{ width: team2Width }} // Width relative to its container (flex-1)
                        ></div>
                    </div>
                </div>

                {/* Team 2 Value (Right) */}
                <span className={`w-12 sm:w-16 text-left text-sm font-bold ${team2Color.replace('bg-', 'text-')}`}>
                    {formatValue(validTeam2Value)}
                </span>
            </div>
        </div>
    );
};

export default StatDualBarChart;