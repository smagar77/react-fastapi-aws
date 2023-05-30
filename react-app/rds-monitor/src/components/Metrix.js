import React from "react";
import { Bar } from "react-chartjs-2";
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

function Metrix({metrix_data, account_name}){
    return(
        <div>
            {metrix_data.map(matrix =>(<div key={matrix.request_id} style={{ maxWidth: "80%", "textAlign": "center", margin: "0 auto" }}>
                <div style={{float: "left"}}><a href={"#top"}>Go to Top^</a></div>
                <h3><label id={matrix["instance_identifier"]}> Account: {matrix["instance_identifier"]}</label></h3>
                <Bar
                    data={{
                        // Name of the variables on x-axies for each bar
                        labels: matrix["MetricDataResults"][0]["Timestamps"].map(formatDate),
                        datasets: [
                        {
                            // Label for bars
                            label: "FreeStorageSpace(in GB)/datetime",
                            // Data or value of your each variable
                            data: matrix["MetricDataResults"][0]["Values"].map(data=>bytesToSize(parseInt(data))),
                            borderWidth: 0.1,
                            borderColor: ["#f55d5d"],
                            backgroundColor: ["#f55d5d"],
                        },
                        ],
                    }}
                    // Height of graph
                    height={80}
                />
            
            </div>))}
        </div>
    )
}
function bytesToSize(bytes) {
    var i = Math.floor(Math.log(bytes) / Math.log(1024)),
    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    return ((bytes / Math.pow(1000, 2)).toFixed(2) * 1)/1000;
}

function formatDate(date_obj) {
    return date_obj.replace('+00:00', '')
}
export default Metrix