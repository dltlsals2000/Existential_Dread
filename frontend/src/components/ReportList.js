import * as React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';

function ReportList() {
    const reports = [
        {
            "id": 1,
            "name": "Report 1",
            "description": "This is report 1",
            "date": "2021-01-01",
            "score": 89
        },
        {
            "id": 2,
            "name": "Report 2",
            "description": "This is report 2",
            "date": "2021-01-02",
            "score": 89
        },
        {
            "id": 3,
            "name": "Report 3",
            "description": "This is report 3",
            "date": "2021-01-03",
            "score": 78
        }
    ];
    
    console.log(reports);
    reports.map((report, index) => {
        console.log(report);
    });

    return (
        <div>
            <Typography>
                Reports
            </Typography>
            {reports.map((report, index) => {
                return (<Card key={index}>
                    <CardContent>
                        <Typography sx={{ fontSize: 14 }} color="text.secondary" gutterBottom>
                          Trust Score: {report.score}
                        </Typography>
                        <Typography variant="h5" component="div">
                          {report.description}
                        </Typography>
                        <Typography sx={{ mb: 1.5 }} color="text.secondary">
                          {report.date}
                        </Typography>
                    </CardContent>
                </Card>)
            })}
        </div>
    )
}

export default ReportList;
