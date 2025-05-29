import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CSVExport = () => {
    const [exportJobs, setExportJobs] = useState([]);
    const [currentJob, setCurrentJob] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Get auth token from localStorage
    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    // API headers with auth token
    const getHeaders = () => ({
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
    });

    // Fetch export history on component mount
    useEffect(() => {
        fetchExportHistory();
    }, []);

    // Poll job status if there's a current job
    useEffect(() => {
        let interval;
        if (currentJob && ['pending', 'processing'].includes(currentJob.status)) {
            interval = setInterval(() => {
                checkJobStatus(currentJob.job_id);
            }, 3000); // Check every 3 seconds
        }
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [currentJob]);

    const fetchExportHistory = async () => {
        try {
            const response = await axios.get(
                'http://localhost:5000/api/export/csv/history',
                { headers: getHeaders() }
            );
            setExportJobs(response.data.export_jobs);
            
            // Check if there's a pending/processing job
            const activeJob = response.data.export_jobs.find(
                job => ['pending', 'processing'].includes(job.status)
            );
            if (activeJob) {
                setCurrentJob(activeJob);
            }
        } catch (err) {
            console.error('Error fetching export history:', err);
        }
    };

    const requestCSVExport = async () => {
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const response = await axios.post(
                'http://localhost:5000/api/export/csv/request',
                {},
                { headers: getHeaders() }
            );

            setCurrentJob({
                job_id: response.data.job_id,
                status: response.data.status
            });
            setSuccess('CSV export requested successfully! You will be notified when it\'s ready.');
            fetchExportHistory();
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to request CSV export');
        } finally {
            setLoading(false);
        }
    };

    const checkJobStatus = async (jobId) => {
        try {
            const response = await axios.get(
                `http://localhost:5000/api/export/csv/status/${jobId}`,
                { headers: getHeaders() }
            );

            const jobData = response.data;
            setCurrentJob(jobData);

            if (jobData.status === 'completed') {
                setSuccess('Your CSV export is ready for download!');
                fetchExportHistory();
            } else if (jobData.status === 'failed') {
                setError(`Export failed: ${jobData.error_message}`);
                setCurrentJob(null);
            }
        } catch (err) {
            console.error('Error checking job status:', err);
        }
    };

    const downloadCSV = async (jobId) => {
        try {
            const response = await axios.get(
                `http://localhost:5000/api/export/download/${jobId}`,
                {
                    headers: getHeaders(),
                    responseType: 'blob'
                }
            );

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `parking_history_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            setSuccess('CSV file downloaded successfully!');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to download CSV file');
        }
    };

    const cancelJob = async (jobId) => {
        try {
            await axios.post(
                `http://localhost:5000/api/export/csv/cancel/${jobId}`,
                {},
                { headers: getHeaders() }
            );
            setCurrentJob(null);
            setSuccess('Export job cancelled successfully');
            fetchExportHistory();
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to cancel job');
        }
    };

    const getStatusBadge = (status) => {
        const statusClasses = {
            pending: 'badge bg-warning',
            processing: 'badge bg-info',
            completed: 'badge bg-success',
            failed: 'badge bg-danger',
            cancelled: 'badge bg-secondary'
        };
        return <span className={statusClasses[status] || 'badge bg-secondary'}>{status}</span>;
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    return (
        <div className="csv-export-container">
            <div className="card">
                <div className="card-header">
                    <h5 className="card-title mb-0">
                        <i className="fas fa-download me-2"></i>
                        Export Parking History
                    </h5>
                </div>
                <div className="card-body">
                    {/* Alert Messages */}
                    {error && (
                        <div className="alert alert-danger alert-dismissible fade show" role="alert">
                            {error}
                            <button 
                                type="button" 
                                className="btn-close" 
                                onClick={() => setError('')}
                            ></button>
                        </div>
                    )}
                    
                    {success && (
                        <div className="alert alert-success alert-dismissible fade show" role="alert">
                            {success}
                            <button 
                                type="button" 
                                className="btn-close" 
                                onClick={() => setSuccess('')}
                            ></button>
                        </div>
                    )}

                    {/* Current Job Status */}
                    {currentJob && ['pending', 'processing'].includes(currentJob.status) && (
                        <div className="alert alert-info">
                            <div className="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>Export in Progress</strong>
                                    <br />
                                    <small>Job ID: {currentJob.job_id}</small>
                                    <br />
                                    Status: {getStatusBadge(currentJob.status)}
                                </div>
                                <div>
                                    {currentJob.status === 'processing' && (
                                        <div className="spinner-border spinner-border-sm me-2" role="status">
                                            <span className="visually-hidden">Loading...</span>
                                        </div>
                                    )}
                                    <button
                                        className="btn btn-sm btn-outline-danger"
                                        onClick={() => cancelJob(currentJob.job_id)}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Export Request Button */}
                    <div className="mb-4">
                        <p className="text-muted">
                            Export your complete parking history as a CSV file. 
                            The file will include reservation details, timestamps, costs, and more.
                        </p>
                        <button
                            className="btn btn-primary"
                            onClick={requestCSVExport}
                            disabled={loading || (currentJob && ['pending', 'processing'].includes(currentJob.status))}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                    Requesting Export...
                                </>
                            ) : (
                                <>
                                    <i className="fas fa-file-csv me-2"></i>
                                    Request CSV Export
                                </>
                            )}
                        </button>
                    </div>

                    {/* Export History */}
                    <div>
                        <h6>Export History</h6>
                        {exportJobs.length === 0 ? (
                            <p className="text-muted">No export history available.</p>
                        ) : (
                            <div className="table-responsive">
                                <table className="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Created</th>
                                            <th>Status</th>
                                            <th>Completed</th>
                                            <th>Expires</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {exportJobs.map((job) => (
                                            <tr key={job.job_id}>
                                                <td>
                                                    <small>{formatDate(job.created_at)}</small>
                                                </td>
                                                <td>{getStatusBadge(job.status)}</td>
                                                <td>
                                                    <small>
                                                        {job.completed_at ? formatDate(job.completed_at) : '-'}
                                                    </small>
                                                </td>
                                                <td>
                                                    <small>
                                                        {job.expires_at ? (
                                                            job.is_expired ? (
                                                                <span className="text-danger">Expired</span>
                                                            ) : (
                                                                formatDate(job.expires_at)
                                                            )
                                                        ) : '-'}
                                                    </small>
                                                </td>
                                                <td>
                                                    {job.status === 'completed' && job.download_url && !job.is_expired ? (
                                                        <button
                                                            className="btn btn-sm btn-outline-success"
                                                            onClick={() => downloadCSV(job.job_id)}
                                                        >
                                                            <i className="fas fa-download me-1"></i>
                                                            Download
                                                        </button>
                                                    ) : job.status === 'failed' ? (
                                                        <small className="text-danger">
                                                            {job.error_message}
                                                        </small>
                                                    ) : (
                                                        <small className="text-muted">-</small>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CSVExport; 