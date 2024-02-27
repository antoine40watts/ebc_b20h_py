<script>
    import { deviceData, deviceParameters, chartDatapoint } from "../stores.js";
    import { Line } from "svelte-chartjs";

    import {
        Chart as ChartJS,
        Title,
        Tooltip,
        Legend,
        LineController,
        LineElement,
        LinearScale,
        PointElement,
    } from "chart.js";

    ChartJS.register(
        Title,
        Tooltip,
        Legend,
        LineController,
        LineElement,
        LinearScale,
        PointElement,
    );

    
    $: chartData = {
        labels: $chartDatapoint.time,
        datasets: [
            {
                label: 'Voltage',
                yAxisID: 'vAxis',
                // fill: true,
                backgroundColor: 'rgba(225, 204,230, .3)',
                borderColor: 'rgb(75, 192, 192)',
                data: $chartDatapoint.voltage,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'Current',
                yAxisID: 'cAxis',
                borderColor: 'rgb(200, 200, 75)',
                data: $chartDatapoint.current,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            },
            {
                label: 'mAh',
                yAxisID: 'mahAxis',
                borderColor: 'rgb(80, 230, 152)',
                data: $chartDatapoint.mah,
                // pointStyle: false,
                pointStyle: 'circle',
                pointRadius: 2,
                pointHoverRadius: 6
            }
        ],
    }


    $: options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                title: { 
                    text: 'Time (s)',
                    display: true,
                },
                type: 'linear',
                min: Math.floor($chartDatapoint.time[0]),
                max: Math.ceil($chartDatapoint.time[$chartDatapoint.time.length - 1]),
            },
            vAxis: {
                title: { 
                    text: 'Voltage',
                    align: 'end',
                    display: true,
                },
                type: 'linear',
                // suggestedMax: 1 + Math.max(...$chartDatapoint.voltage),
                beginAtZero: true,
            },
            cAxis: {
                title: { 
                    text: 'Amp',
                    align: 'end',
                    display: true,
                },
                grid: {
                    drawOnChartArea: false, // only want the grid lines for one axis to show up
                },
                type: 'linear',
                // suggestedMax: 1 + Math.max(...$chartDatapoint.current),
                beginAtZero: true,
            },
            mahAxis: {
                title: { 
                    text: 'mAh',
                    align: 'end',
                    display: true,
                },
                type: 'linear',
                position: 'right',
                beginAtZero: true,
            },
        },
        animation: false,
    };
</script>

<div class="container">
    <div class="chart-container">
        <Line options={options} data={chartData} />
    </div>
</div>


<style>
    .container {
        min-width: 400px;
        /* background-color: #646cffaa; */
        display: flex;
        flex-grow: 16;
        flex-direction: row;
        justify-content: center;
        align-items: center;
    }
    .chart-container {
        flex-grow: 1;
        width: 1px; /* Works because of flex-grow */
        height: 100%;
    }
    

    @media print {
        .container {
            /* transform: rotate(90deg); */
            /* display: flow; */
            position: absolute;
            top: 120px;
            left: 0;
        }
    }
</style>