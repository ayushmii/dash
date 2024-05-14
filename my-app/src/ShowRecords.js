import React, { useState, useEffect, memo } from 'react';
import axios from 'axios';

const RecordsTable = memo(({ infoId, shouldRefresh }) => {
  const [records, setRecords] = useState([]);
  const [showRecords, setShowRecords] = useState(true);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await axios.get(`http://localhost:5354/infoid_records?info_id=${infoId}`);
        console.log('Records fetched:', response.data);
        setRecords(response.data);
      } catch (error) {
        console.error('Error fetching records:', error);
      }
    };
  
    fetchRecords();
  }, [infoId, shouldRefresh]);
  

  const toggleShowRecords = () => {
    setShowRecords(!showRecords);
  };

  return (
    <div>
      <button className="btn btn-primary mb-2" onClick={toggleShowRecords}>{showRecords ? 'Hide Records' : 'Show Records'}</button>
      {showRecords && (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>SR No</th>
              <th>Disease Desc</th>
              <th>Disease</th>
              <th>Visits</th>
              <th>Patients</th>
              <th>Discharge Summaries</th>
              <th>DS Patients</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                <td>{record[2]}</td>
                <td>{record[3]}</td>
                <td>{record[4]}</td>
                <td>{record[5]}</td>
                <td>{record[6]}</td>
                <td>{record[7]}</td>
                <td>{record[8]}</td>
                <td>{record[9]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
});

export default RecordsTable;
