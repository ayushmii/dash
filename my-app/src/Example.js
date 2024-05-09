import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Modal, Button, Form } from 'react-bootstrap';

function App() {
  const [latestRecords, setLatestRecords] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    shortDesc: '',
    dateFrom: '',
    dateTo: '',
    diseaseNames: ''
  });

  useEffect(() => {
    fetchLatestRecords();
  }, []);

  const fetchLatestRecords = async () => {
    try {
      const response = await axios.get(`http://localhost:${process.env.DISEASE_APP_PORT}/latest_records`);
      setLatestRecords(response.data);
    } catch (error) {
      console.error('Error fetching latest records:', error);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value
    }));
  };

  const handleNewSearch = () => {
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
  };

  const handleProceed = async () => {
    const { shortDesc, dateFrom, dateTo, diseaseNames } = formData;
    const diseaseNameList = diseaseNames.split(',').map(name => name.trim());

    try {
      // Add a new record to the patient_counts_info table
      const infoResponse = await axios.post(`http://localhost:${process.env.DISEASE_APP_PORT}/patient_counts_info`, {
        short_desc: shortDesc,
        data_from: dateFrom,
        data_upto: dateTo,
        status: 'Processing'
      });
      const newInfoId = infoResponse.data.info_id;

      // Add new records to the patient_counts_disease table
      const diseasePromises = diseaseNameList.map(async (diseaseName, index) => {
        const diseaseResponse = await axios.post(`http://localhost:${process.env.DISEASE_APP_PORT}/patient_counts_disease`, {
          info_id: newInfoId,
          sr_no: index + 1,
          disease_desc: diseaseName,
          disease: diseaseName,
          visits: null,
          patients: null,
          discharge_summaries: null,
          ds_patients: null,
          status: 'Processing'
        });
        return diseaseResponse.data;
      });
      const newDiseaseRecords = await Promise.all(diseasePromises);

      // Call the backend API to process the disease counts
      for (const diseaseName of diseaseNameList) {
        try {
          const response = await axios.get(`http://localhost:${process.env.QUERRY_SERVER_PORT}/disease_counts?disease_name=${diseaseName}&date_from=${dateFrom}&date_to=${dateTo}`);
          console.log(response.data);
          // Update the database with the response data
        } catch (error) {
          console.error('Error processing disease counts:', error);
        }
      }

      setShowModal(false);
      fetchLatestRecords();
    } catch (error) {
      console.error('Error adding new records:', error);
    }
  };

  return (
    <div className="App">
      <h1>Patient Counts Disease</h1>
      <button onClick={handleNewSearch}>New Search</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Info ID</th>
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
          {latestRecords.map((record) => (
            <tr key={record.id}>
              <td>{record.id}</td>
              <td>{record.info_id}</td>
              <td>{record.sr_no}</td>
              <td>{record.disease_desc}</td>
              <td>{record.disease}</td>
              <td>{record.visits}</td>
              <td>{record.patients}</td>
              <td>{record.discharge_summaries}</td>
              <td>{record.ds_patients}</td>
              <td>{record.status}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <Modal show={showModal} onHide={handleModalClose}>
        {/* <Modal.Header closeButton>
          <Modal.Title>New Search</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group controlId="formShortDesc">
              <Form.Label>Short Description</Form.Label>
              <Form.Control
                type="text"
                name="shortDesc"
                value={formData.shortDesc}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDateFrom">
              <Form.Label>Date From</Form.Label>
              <Form.Control
                type="date"
                name="dateFrom"
                value={formData.dateFrom}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDateTo">
              <Form.Label>Date To</Form.Label>
              <Form.Control
                type="date"
                name="dateTo"
                value={formData.dateTo}
                onChange={handleInputChange}
              />
            </Form.Group>
            <Form.Group controlId="formDiseaseNames">
              <Form.Label>Disease Names (separated by commas)</Form.Label>
              <Form.Control
                type="text"
                name="diseaseNames"
                value={formData.diseaseNames}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleModalClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleProceed}>
            Proceed
          </Button>
        </Modal.Footer> */}
      </Modal>
    </div>
  );
}

export default App;
