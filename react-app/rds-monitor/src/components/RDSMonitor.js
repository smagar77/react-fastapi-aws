import React, {useState, useEffect} from 'react'
import { useParams } from "react-router-dom";
import axios from 'axios'

import Metrix from './Metrix'


function RDSMonitor({base_url}){
    const {account_name} = useParams()
    const [instances, setInstances] = useState([])
    const [metrix, setMetrix] = useState([])

    useEffect(()=>{
        console.log(account_name)
        axios.get(base_url+"/rdsinstance?account_name="+account_name).then(monitor=>{
            setInstances(monitor.data)
        }).catch(error => {
            console.log(error)
        })
    }, [account_name])
    useEffect(()=>{
        axios.get(base_url+"/rdsmatrix?account_name="+account_name).then(metrix=>{
            setMetrix(metrix.data)
        }).catch(error => {
            console.log(error)
        })
    }, [account_name])

    return(
        <div className='table-container'>
            <label id={"top"}>&nbsp;</label>
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
                        <th>Maintenance Window(UTC)</th>
                        <th>Backup Window(UTC)</th>
                        <th>Automated Backups(Days)</th>
                        <th>Storage(GB)</th>
                        <th>Maximum Storage Threshold(GB)</th>
                        <th>Engine</th>
                        <th>Multi Az</th>
                    </tr>
                </thead>
                <tbody>
                    {instances.map(instance =>(
                        <tr key={instance.id}>
                            <td>{instance.account_name}</td>
                            <td>{instance.modified_at}</td>
                            <td>{instance.instance_class}</td>
                            <td><a href={"#"+instance.instance_identifier}>{instance.instance_identifier}</a></td>
                            <td>{instance.instance_status}</td>
                            <td>{instance.maintenance_window}</td>
                            <td>{instance.backup_window}</td>
                            <td>{instance.automated_backups}</td>
                            <td>{instance.storage}</td>
                            <td>{instance.maximum_storage_threshold}</td>
                            <td>{instance.engine}</td>
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