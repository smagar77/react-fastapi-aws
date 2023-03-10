import React, {useState, useEffect} from 'react'
import { useParams } from "react-router-dom";
import axios from 'axios'

import Metrix from './Metrix'


function RDSMonitor(){
    const {account_name} = useParams()
    const [instances, setInstances] = useState([])
    const [metrix, setMetrix] = useState([])

    useEffect(()=>{
        console.log(account_name)
        axios.get("http://127.0.0.1:8080/rdsinstance?account_name="+account_name).then(monitor=>{
            setInstances(monitor.data)
        }).catch(error => {
            console.log(error)
        })
    }, [account_name])

    useEffect(()=>{
        axios.get("http://127.0.0.1:8080/rdsmatrix?account_name="+account_name).then(metrix=>{
            setMetrix(metrix.data)
        }).catch(error => {
            console.log(error)
        })
    }, [account_name])

    return(
        <div className='table-container'>
            <br />
            <h2>{account_name}</h2>
            <table cellSpacing="0" cellPadding="10" border="1">
                <thead>
                    <tr>
                        <th>Account Name</th>
                        <th>Updated Date</th>
                        <th>DB Instance Class</th>
                        <th>DB Instance Identifier</th>
                        <th>DB Instance Status</th>
                        <th>Maintenance Window</th>
                        <th>Backup Window</th>
                        <th>Automated Backups</th>
                        <th>Storage</th>
                        <th>Maximum Storage Threshold</th>
                        <th>Multi Az</th>
                    </tr>
                </thead>
                <tbody>
                    {instances.map(instance =>(
                        <tr key={instance.id}>
                            <td>{instance.account_name}</td>
                            <td>{instance.modified_at}</td>
                            <td>{instance.instance_class}</td>
                            <td>{instance.instance_identifier}</td>
                            <td>{instance.instance_status}</td>
                            <td>{instance.maintenance_window}</td>
                            <td>{instance.backup_window}</td>
                            <td>{instance.automated_backups}</td>
                            <td>{instance.storage}</td>
                            <td>{instance.maximum_storage_threshold}</td>
                            <td>{instance.multi_az}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div>
                <br/>
                <br/>
                <Metrix metrix_data={metrix} account_name={account_name} />
            </div>
        </div>
    )
}

export default RDSMonitor