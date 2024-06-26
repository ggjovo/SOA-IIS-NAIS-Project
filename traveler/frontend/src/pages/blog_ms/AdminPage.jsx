import React, { useState, useEffect } from "react";
import axios from "axios";
import { Line } from 'react-chartjs-2';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { Box, Button, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import Checkbox from '@mui/material/Checkbox';
import { Menu, MenuItem, IconButton } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import '../../css/admin-page.css';

// Register Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const AdminPage = () => {
    const [platformReviews, setPlatformReviews] = useState([]);
    const [averageRatingByDay, setAverageRatingByDay] = useState({});
    const [filteredRatingData, setFilteredRatingData] = useState({});
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState({
        isLoggedIn: false,
        username: '',
    });
    const navigate = useNavigate();
    const [selectedReviews, setSelectedReviews] = useState([]);
    const [sortOrder, setSortOrder] = useState('none');
    const [selectedRole, setSelectedRole] = useState('all');
    const [selectedRatings, setSelectedRatings] = useState([]);
    const [anchorEl, setAnchorEl] = useState(null);
    const open = Boolean(anchorEl);

    const [popularPosts, setPopularPosts] = useState([]);
    const [popularBlogs, setPopularBlogs] = useState([]);
    const [mostActiveUsers, setMostActiveUsers] = useState([]);

    const [includePopularPosts, setIncludePopularPosts] = useState(false);
    const [includePopularBlogs, setIncludePopularBlogs] = useState(false);
    const [includeMostActiveUsers, setIncludeMostActiveUsers] = useState(false);

    useEffect(() => {
        const checkLoginStatus = async () => {
            try {
                const { data } = await axios.get('http://localhost:8082/checklogin', {
                    withCredentials: true,
                });

                if (data.loggedIn) {
                    setUser({
                        isLoggedIn: true,
                        username: data.username,
                    });
                } else {
                    navigate('/login');
                }
            } catch (error) {
                console.error('Error checking login status:', error);
            } finally {
                setLoading(false);
            }
        };

        checkLoginStatus();
    }, [navigate]);

    useEffect(() => {
        fetchPlatformReviews();
        fetchAverageRatingByDay();
        fetchPopularPosts();
        fetchPopularBlogs();
        fetchMostActiveUsers();
    }, []);

    useEffect(() => {
        filterChartData();
    }, [startDate, endDate, averageRatingByDay]);

    const fetchPlatformReviews = async () => {
        try {
            const response = await axios.get(
                "http://localhost:8083/admin/platform_reviews",
                { withCredentials: true } // Set withCredentials to true
            );
            setPlatformReviews(response.data.platform_reviews);
        } catch (error) {
            console.error("Error fetching platform reviews:", error);
        }
    };

    const fetchAverageRatingByDay = async () => {
        try {
            const response = await axios.get("http://localhost:8083/admin/average_rating_by_day", { withCredentials: true });
            setAverageRatingByDay(response.data);
        } catch (error) {
            console.error("Error fetching average rating by day:", error);
        }
    };

    const fetchPopularPosts = async () => {
        try {
            const response = await axios.get("http://localhost:8085/get_most_popular_posts");
            setPopularPosts(response.data);
        } catch (error) {
            console.error("Error fetching popular posts:", error);
        }
    };

    const fetchPopularBlogs = async () => {
        try {
            const response = await axios.get("http://localhost:8085/get_most_popular_blogs");
            setPopularBlogs(response.data);
        } catch (error) {
            console.error("Error fetching popular blogs:", error);
        }
    };

    const fetchMostActiveUsers = async () => {
        try {
            const response = await axios.get("http://localhost:8085/get_most_active_user");
            setMostActiveUsers(response.data);
        } catch (error) {
            console.error("Error fetching most active users:", error);
        }
    };

    const filterChartData = () => {
        if (startDate && endDate) {
            const filteredData = {};
            for (const [date, rating] of Object.entries(averageRatingByDay)) {
                if (new Date(date) >= startDate && new Date(date) <= endDate) {
                    filteredData[date] = rating;
                }
            }
            setFilteredRatingData(filteredData);
        } else {
            setFilteredRatingData(averageRatingByDay);
        }
    };

    const handleBlockUser = async (userId, isBlocked) => {
        let action;
        if (isBlocked) {
            action = 'unblock';
        } else {
            action = 'block';
        }

        try {
            const response = await axios.put(
                `http://localhost:8083/admin/block_user/${userId}`,
                {},
                { withCredentials: true } // Set withCredentials to true
            );
            const message = isBlocked ? `User with ID ${userId} unblocked successfully.` : `User with ID ${userId} blocked successfully.`;
            alert(message);
            fetchPlatformReviews(); // Refresh the platform reviews
        } catch (error) {
            console.error(`Error ${action}ing user:`, error);
        }
    };

    const handleCheckboxChange = (userId, isChecked) => {
        if (isChecked) {
            setSelectedReviews([...selectedReviews, userId]);
        } else {
            setSelectedReviews(selectedReviews.filter(id => id !== userId));
        }
    };

    const generatePDF = async () => {
        const input = document.getElementById('chart-container');
        const canvas = await html2canvas(input);
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');

        pdf.setFontSize(20);
        pdf.text('PLATFORM RATING REPORT', 10, 10);
        pdf.setFontSize(12);
        pdf.text(`for dates: ${startDate ? startDate.toISOString().split('T')[0] : 'N/A'} - ${endDate ? endDate.toISOString().split('T')[0] : 'N/A'}`, 10, 20);
        pdf.text(`Generated for admin: ${user.username}`, 10, 30);
        const avgRating = Object.values(filteredRatingData).reduce((a, b) => parseFloat(a) + parseFloat(b), 0) / Object.values(filteredRatingData).length || 0;
        pdf.text(`Average rating for this time span is: ${avgRating.toFixed(2)}`, 10, 40);
        pdf.text('Chart showing rating per days:', 10, 50);
        pdf.addImage(imgData, 'PNG', 10, 60, 190, 80);

        // Include selected reviews in PDF
        pdf.setFontSize(16);
        pdf.text('Selected Reviews:', 10, 160);

        // Loop through selected reviews and add them to PDF
        let yPosition = 170;
        let pageHeight = pdf.internal.pageSize.height;
        selectedReviews.forEach((reviewId, index) => {
            const review = platformReviews.find(review => review.user_id === reviewId);
            if (review) {
                if (yPosition + 60 > pageHeight) {
                    pdf.addPage(); // Add a new page if the current one is filled
                    yPosition = 10; // Reset yPosition for the new page
                }
                pdf.setFontSize(12);
                pdf.text(`Author: ${review.username} | Role: ${review.user_role}`, 10, yPosition); // Combined username and role
                pdf.text(`Rating: ${review.rating}`, 10, yPosition + 10);
                pdf.text(`Comment: ${review.comment}`, 10, yPosition + 20);
                pdf.line(10, yPosition + 30, 200, yPosition + 30); // Horizontal line between reviews
                yPosition += 60; // Increase yPosition for the next review
            }
        });

        // Add popular posts table if included
        if (includePopularPosts) {
            pdf.autoTable({
                startY: yPosition + 20,
                head: [['Post Title', 'Total Likes']],
                body: popularPosts.map(post => [post.postTitle, post.totalLikes]),
                margin: { top: 10 }
            });
            yPosition = pdf.lastAutoTable.finalY + 10;
        }

        // Add popular blogs table if included
        if (includePopularBlogs) {
            pdf.autoTable({
                startY: yPosition + 20,
                head: [['Blog Title', 'Total Likes']],
                body: popularBlogs.map(blog => [blog.blogTitle, blog.totalLikes]),
                margin: { top: 10 }
            });
            yPosition = pdf.lastAutoTable.finalY + 10;
        }

        // Add most active users table if included
        if (includeMostActiveUsers) {
            pdf.autoTable({
                startY: yPosition + 20,
                head: [['User Name', 'Total Activity']],
                body: mostActiveUsers.map(user => [user.userName, user.totalActivity]),
                margin: { top: 10 }
            });
        }

        // Save the PDF
        pdf.save("platform_rating_report.pdf");
    };

    const handleLogout = async () => {
        try {
            const { status } = await axios.get('http://localhost:8082/logout', {
                withCredentials: true,
            });
            if (status === 200) {
                console.log('Logging out');
                navigate('/login');
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    };

    const filteredReviews = platformReviews.filter(review => {
        const roleMatch = selectedRole === 'all' || review.user_role === selectedRole;
        const ratingMatch = selectedRatings.length === 0 || selectedRatings.includes(review.rating);
        return roleMatch && ratingMatch;
    });

    const sortedAndFilteredReviews = [...filteredReviews].sort((a, b) => {
        if (sortOrder === 'asc') {
            return a.rating - b.rating;
        } else if (sortOrder === 'desc') {
            return b.rating - a.rating;
        } else {
            return 0; // No sorting, keep default order
        }
    });

    const platformReviewList = sortedAndFilteredReviews.map((review, index) => {
        let action;
        if (review.blocked) {
            action = 'unblock';
        } else {
            action = 'block';
        }

        return (
            <div key={index} className={`review ${review.blocked ? 'blocked' : 'not_blocked'}`}>
                <p>Username: {review.username}</p>
                <p>User Role: {review.user_role}</p>
                <p>Rating: {review.rating}</p>
                <p>Comment: {review.comment}</p>
                <p>Blocked: {review.blocked ? 'Yes' : 'No'}</p>
                <div style={{ display: 'flex', alignItems: 'center' }}> {/* Adjust styles for alignment */}
                    <button onClick={() => handleBlockUser(review.user_id, review.blocked)}>
                        {action === 'block' ? 'Block User' : 'Unblock User'}
                    </button>
                    <label style={{ marginLeft: '10px' }}>Include review in report:</label>
                    <Checkbox
                        checked={selectedReviews.includes(review.user_id)}
                        onChange={(e) => handleCheckboxChange(review.user_id, e.target.checked)}
                    />
                </div>
                <hr />
            </div>
        );
    });

    const chartData = {
        labels: Object.keys(filteredRatingData),
        datasets: [
            {
                label: 'Average Rating by Day',
                data: Object.values(filteredRatingData),
                fill: false,
                backgroundColor: 'rgb(75, 192, 192)',
                borderColor: 'rgba(75, 192, 192, 0.2)',
            },
        ],
    };

    const chartOptions = {
        scales: {
            y: {
                min: 0,
                max: 6,
            },
        },
    };

    const uncheckAllCheckboxes = () => {
        setSelectedReviews([]); // Clear the selected reviews array
    };

    const handleSortChange = (e) => {
        setSortOrder(e.target.value);
    };

    const handleRoleChange = (e) => {
        setSelectedRole(e.target.value);
    };

    const handleRatingChange = (e) => {
        const rating = parseInt(e.target.value, 10);
        if (e.target.checked) {
            setSelectedRatings([...selectedRatings, rating]);
        } else {
            setSelectedRatings(selectedRatings.filter(r => r !== rating));
        }
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    return (
        <div className="admin-page" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: 'auto auto', gap: '20px' }}>
            <div className="reviews-section" style={{ gridColumn: '1 / 2', gridRow: '1 / 2' }}>
                <div className="filter-options">
                    <h2>Platform Reviews</h2>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                        <div>
                            <label>Sort by Rating: </label>
                            <select onChange={handleSortChange} value={sortOrder}>
                                <option value="none">-- No Sort --</option>
                                <option value="asc">Ascending</option>
                                <option value="desc">Descending</option>
                            </select>
                        </div>
                        <div>
                            <label>Filter by Role: </label>
                            <select onChange={handleRoleChange} value={selectedRole}>
                                <option value="all">-- All Roles --</option>
                                <option value="admin">Admin</option>
                                <option value="guide">Guide</option>
                                <option value="tourist">Tourist</option>
                            </select>
                        </div>
                        <label>Filter by Rating: </label>
                        <IconButton
                            aria-controls={open ? 'rating-menu' : undefined}
                            aria-haspopup="true"
                            aria-expanded={open ? 'true' : undefined}
                            onClick={handleClick}
                        >
                            <FilterListIcon />
                        </IconButton>
                        <Menu
                            id="rating-menu"
                            anchorEl={anchorEl}
                            open={open}
                            onClose={handleClose}
                            MenuListProps={{
                                'aria-labelledby': 'filter-button',
                            }}
                        >
                            <MenuItem>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                                    {[1, 2, 3, 4, 5].map(rating => (
                                        <label key={rating} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                            <input
                                                type="checkbox"
                                                value={rating}
                                                checked={selectedRatings.includes(rating)}
                                                onChange={handleRatingChange}
                                            />
                                            {rating}
                                        </label>
                                    ))}
                                </div>
                            </MenuItem>
                        </Menu>
                    </div>
                </div>
                {platformReviewList}
            </div>
            
            <div className="chart-section" style={{ gridColumn: '2 / 3', gridRow: '1 / 2' }}>
                <h2>Average Rating by Day</h2>
                <div className="date-picker">
                    <DatePicker
                        selected={startDate}
                        onChange={date => setStartDate(date)}
                        selectsStart
                        startDate={startDate}
                        endDate={endDate}
                        placeholderText="Select start date"
                    />
                    <DatePicker
                        selected={endDate}
                        onChange={date => setEndDate(date)}
                        selectsEnd
                        startDate={startDate}
                        endDate={endDate}
                        minDate={startDate}
                        placeholderText="Select end date"
                    />
                </div>
                <div id="chart-container">
                    <Line data={chartData} options={chartOptions} />
                </div>
                <Button variant="contained" onClick={generatePDF} style={{ marginRight: '10px' }}>Download as PDF</Button>
                <Button variant="contained" onClick={uncheckAllCheckboxes}>Uncheck All Checkboxes</Button>
            </div>
    
            <div style={{ gridColumn: '1 / 2', gridRow: '2 / 3', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginTop: '-35px' }}>
                <h2>Include additional data in report:</h2>
                <label>
                    <Checkbox
                        checked={includePopularBlogs}
                        onChange={(e) => setIncludePopularBlogs(e.target.checked)}
                    />
                    Include most popular blogs
                </label>
                <label>
                    <Checkbox
                        checked={includePopularPosts}
                        onChange={(e) => setIncludePopularPosts(e.target.checked)}
                    />
                    Include most popular posts
                </label>
                <label>
                    <Checkbox
                        checked={includeMostActiveUsers}
                        onChange={(e) => setIncludeMostActiveUsers(e.target.checked)}
                    />
                    Include most active users
                </label>
            </div>
        </div>
    );
    
    
};

export default AdminPage;
