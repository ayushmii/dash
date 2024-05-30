import React, { useState, useEffect, memo } from 'react';
import axios from 'axios';
import { TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions } from '@material-ui/core';
import './ShowRecords.css';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
const diseaseAppPort = process.env.REACT_APP_DISEASE_APP_PORT;
const dashboardAppPort = process.env.REACT_APP_DASHBOARD_APP_PORT;
const queryServerPort = process.env.REACT_APP_QUERY_SERVER_PORT;
const patientCountStackPort = process.env.PATIENT_COUNT_STACK_PORT;
const patientCountPort = process.env.PATIENT_COUNT_PORT;

const handleDownloadPDF = async () => {
  const input = document.querySelector('.table');
  const canvas = await html2canvas(input, { scale: 2 });
  const imgData = canvas.toDataURL('image/png', 1.0);
  const pdf = new jsPDF('p', 'mm', 'a4');
  const imgProps = pdf.getImageProperties(imgData);
  const pdfWidth = pdf.internal.pageSize.getWidth();
  const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
  pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
  pdf.save('table.pdf');
};

const formatDate = (dateStr) => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const date = new Date(dateStr);
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  return `${month} '${year.toString().slice(-2)}`;
};
const RecordsTable = memo(({
  recordType,
  infoId,
  shouldRefresh,
  additionalDiseaseNames,
  handleAdditionalDiseaseNamesChange,
  handleProcessAdditionalDiseases,
  formData,
  classes,
  updateShortDesc,
  handleSetInfoId,
  isNewSearch
}) => {
  const [records, setRecords] = useState([]);
  const [showRecords, setShowRecords] = useState(true);
  const [dateRange, setDateRange] = useState(null); // New state for date range
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const formatDateNew = (dateStr) => {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Adding 1 to get the correct month (0-indexed)
    const day = String(date.getDate()).padStart(2, '0');
    return `${day}/${month}/${year}`;
  };


  useEffect(() => {
    // Add logic here to fetch data or perform any actions when infoId changes
    console.log('infoId changed:', infoId);
  }, [infoId]);
  useEffect(() => {
    const getUpdatedShortDesc = () => {
      // Determine the updated value for formData.shortDesc based on the records
      const updatedShortDesc = records.length > 0 ? records[0][3] : ''; // Assuming the disease name is in the 5th column

      // Call the updateShortDesc callback function to update formData.shortDesc in the App component
      updateShortDesc(updatedShortDesc);
    };

    getUpdatedShortDesc();
  }, [records]);

  const fetchRecords = async () => {
    try {
      console.log(infoId, recordType)
      let response;
      if (infoId) {
        console.log(infoId);
        console.log(recordType);
        response = await axios.get(`http://localhost:${diseaseAppPort}/infoid_records?info_id=${infoId}`);
        // Fetch date range from the backend
        const dateRangeResponse = await axios.get(`http://localhost:${diseaseAppPort}/info_records?info_id=${infoId}`);
        console.log('Date range response:', dateRangeResponse.data)
        if (dateRangeResponse.data.length > 0) {
          const data_from = dateRangeResponse.data[0][3];
            const data_upto = dateRangeResponse.data[0][4];
            setDateRange({ from: data_from, to: data_upto });
            
        }
        
      }
      else if (recordType === 'completed') {
        response = await axios.get(`http://localhost:${diseaseAppPort}/latest_records_completed`);
        if (response.data.length > 0) {
          const firstRecord = response.data[0];
          const fetchedInfoId = firstRecord[1]; // Assuming info_id is in the second column
          handleSetInfoId(fetchedInfoId);
          const dateRangeResponse = await axios.get(`http://localhost:${diseaseAppPort}/info_records?info_id=${fetchedInfoId}`);
        console.log('Date range response:', dateRangeResponse.data)
        if (dateRangeResponse.data.length > 0) {
          if (dateRangeResponse.data.length > 0) {
            const data_from = dateRangeResponse.data[0][3];
            const data_upto = dateRangeResponse.data[0][4];
            setDateRange({ from: data_from, to: data_upto });
          }
        }
        }
      } else if (recordType === 'processing') {
        
      console.log("SDS")
        response = await axios.get(`http://localhost:${diseaseAppPort}/latest_records_processing`);
        if (response.data.length > 0) {
          const firstRecord = response.data[0];
          const fetchedInfoId = firstRecord[1]; // Assuming info_id is in the second column
          handleSetInfoId(fetchedInfoId);
          const dateRangeResponse = await axios.get(`http://localhost:${diseaseAppPort}/info_records?info_id=${fetchedInfoId}`);
          console.log('Date range response:', dateRangeResponse.data)
          if (dateRangeResponse.data.length > 0) {
            console.log("efsfsdf")
            const data_from = dateRangeResponse.data[0][3];
            const data_upto = dateRangeResponse.data[0][4];
            setDateRange({ from: data_from, to: data_upto });
          }
          
        }
        else {
          console.log("SSSS");
          const data_from = null;
          const data_upto = null;
          setDateRange({ from: data_from, to: data_upto });
        } 
      }

      if (response) {
        console.log('Records fetched:', response.data);
        setRecords(response.data);
      }
    } catch (error) {
      console.error('Error fetching records:', error);
    }
  };
  useEffect(() => {
  
    fetchRecords();
  }, [infoId, shouldRefresh, recordType]);

 
  const handleDeleteRecord = async (srNo) => {
    try {
      const response = await axios.delete(`http://localhost:${diseaseAppPort}/delete_record`, {
        headers: {
          'Content-Type': 'application/json'
        },
        data: {
          info_id: infoId,
          sr_no: srNo
        }
      });
      console.log('Record deleted:', response.data);
      setShowDeleteConfirmation(true); // Show delete confirmation popup
      fetchRecords();
    } catch (error) {
      console.error('Error deleting record:', error);
    }
  };
  
  const handleCloseDeleteConfirmation = () => {
    setShowDeleteConfirmation(false); // Close delete confirmation popup
  };
  return (
    <div>
      <Dialog open={showDeleteConfirmation} onClose={handleCloseDeleteConfirmation}>
        <DialogTitle>Record Deleted</DialogTitle>
        <DialogContent>The record has been successfully deleted.</DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteConfirmation} color="primary" >
            OK
          </Button>
        </DialogActions>
      </Dialog>
      {showRecords && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            {dateRange && (
              <h4>
                ({formatDate(dateRange.from)} to {formatDate(dateRange.to)})
              </h4>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <h5>
              <div style={{ marginRight: '12px' }}>Dated:</div>
              <div>{records[0]?.[10] ? formatDateNew(records[0][10]) : ''}</div>
            </h5>
          </div>
        </div>
      )}
      {true &&( // Add this condition
          <div>
            <TextField
              label="Add Disease(s) (separated by commas)"
              value={additionalDiseaseNames}
              onChange={handleAdditionalDiseaseNamesChange}
              variant="outlined"
            />
           <button className='btn-9' onClick={handleProcessAdditionalDiseases}>
          Process Additional Diseases
        </button>
          </div>
        )}
        <button onClick={handleDownloadPDF} className="download-button">
  <span className="material-symbols-outlined">picture_as_pdf</span>
</button>
<button onClick={fetchRecords} className="refresh-button">
  <span className="material-symbols-outlined">refresh</span> Refresh
</button>
      {showRecords && (
        <table className="table table-striped">
          <thead>
            <tr>
              <th>DISEASE</th>
              <th>VISITS <br /> (Based on primary diagnosis on arrival)</th>
              <th>PATIENTS <br />(Distinct based on visits)</th>
              <th>DISCHARGE SUMMARIES</th>
              <th>DS PATIENTS<br />(Distinct based on discharge summaries)</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {records.map((record, index) => (
              <tr key={record[0]}>
                <td>{record[4]}</td>
                <td>{record[5]}</td>
                <td>{record[6]}</td>
                <td>{record[7]}</td>
                <td>{record[8]}</td>
                <td>
                  <span
                    className="material-symbols-outlined"
                    style={{
                      cursor: 'pointer',
                      color: '#666',
                      transition: 'color 0.3s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.color = 'red'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#666'}
                    onClick={() => handleDeleteRecord(record[2])}
                  >
                    delete
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
});

export default RecordsTable;