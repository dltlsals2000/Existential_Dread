import * as React from 'react';
import { Chart } from "react-google-charts";
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

function getAreaReports(timeRangeStart, timeRangeEnd, keyword) {
    // Call the API.
    
    // Mocked for now. Returns a list of areas with reports made within the time range.
    const response = [
        {
            "id": 1,
            "area": "Alberta",
            "reports": [
                {
                    "id": 1,
                    "latitude": 49.2827,
                    "longitude": -123.1207,
                    "date": "2023-05-01"
                },
                {
                    "id": 2,
                    "latitude": 49.2826,
                    "longitude": -123.1203,
                    "date": "2023-05-04"
                },
            ],
        },
        {
            "id": 2,
            "area": "Saskatchewan",
            "reports": [
                {
                    "id": 1,
                    "latitude": 49.2826,
                    "longitude": -123.1203,
                    "date": "2023-05-04"
                },
            ],
        },
    ];
    
    return response;
}

function Map() {
    const [startDate, setStartDate] = React.useState(dayjs('2022-04-17'));
    const [endDate, setEndDate] = React.useState(dayjs('2022-04-21'));
    const initialData = [["Province", "Reports"]];
    let data = initialData;
    const keyword = "fire";
    const defaultView = true;
    
    React.useEffect(() => {
        const areas = getAreaReports(startDate, endDate, keyword);
        data = initialData;
        for (let i = 0; i < areas.length; i++) {
            console.log(areas[i]);
            data.push([areas[i].area, areas[i].reports.length]);
        }
    }, [startDate, endDate]);
    
    // Number of open source wildfire reports.
    const options = {
        region: "CA",
        displayMode: "regions",
        resolution: "provinces",
        colorAxis: { colors: ["#00853f", "#e31b23", "black"] },
        backgroundColor: "#81d4fa",
        datalessRegionColor: "#f5f5f5",
        defaultColor: "#f5f5f5",
    };

    return (
        <div>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DatePicker
                    value={startDate}
                    onChange={(newValue) => setStartDate(newValue)}
                />
                <DatePicker
                    value={endDate}
                    onChange={(newValue) => setEndDate(newValue)}
                />
            </LocalizationProvider>
            {defaultView ? (
                <Chart
                  chartEvents={[
                    {
                      eventName: "select",
                      callback: ({ chartWrapper }) => {
                        const chart = chartWrapper.getChart();
                        const selection = chart.getSelection();
                        if (selection.length === 0) return;
                        const region = data[selection[0].row + 1];
                        console.log("Selected : " + region);
                      },
                    },
                  ]}
                  chartType="GeoChart"
                  width="100%"
                  height="400px"
                  data={data}
                  options={options}
                />
            ) : (
                <Chart
                  chartEvents={[
                    {
                      eventName: "select",
                      callback: ({ chartWrapper }) => {
                        const chart = chartWrapper.getChart();
                        const selection = chart.getSelection();
                        if (selection.length === 0) return;
                        const region = data[selection[0].row + 1];
                        console.log("Selected : " + region);
                        defaultView = false;
                      },
                    },
                  ]}
                  chartType="GeoChart"
                  width="50%"
                  height="400px"
                  data={data}
                  options={options}
                />
            )
            }
        </div>
        
    );
}

export default Map;
