import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginForm from './pages/Login';
import HomePage from './pages/HomePage';
import Nav from './components/Nav';
import AddTourPage from './pages/TourCreation';
import TourList from './pages/TourList';
import ViewToursTourist from './pages/ViewToursTourist'
import StartTour from './pages/StartTour'
import './App.css';
import ViewBlogs from './pages/blog_ms/ViewBlogs';
import ViewBlog from './pages/blog_ms/ViewBlog';
import ViewPost from './pages/blog_ms/ViewPost';
import CreateBlog from './pages/blog_ms/CreateBlog';
import RatePlatform from './pages/blog_ms/RatePlatform';
import CheckCreateBlog from './pages/blog_ms/CheckCreateBlog'
import AdminPage from "./pages/blog_ms/AdminPage";
import RegistrationForm from "./pages/Registration";


function App() {
  return (
    <div className="App">
    <BrowserRouter>
       <Nav />
     <main className='form-signin'>
     <Routes>
       <Route path='/' element={<HomePage />}/>
       <Route path='/login' element={<LoginForm />}/>
       <Route path='/create-tour' element={<AddTourPage />} />
       <Route path='/tourist-page' element={<ViewToursTourist />}/>
       <Route path='/start-tour' element={<StartTour />}/>
       <Route path='/view-tours' element={<TourList />} />
       <Route path='/all-blogs' element={<ViewBlogs />} />
       <Route path='/blog/:id' element={<ViewBlog/>} />
       <Route path='blog/:id/post/:id' element={<ViewPost />} />
       <Route path='create-blog' element={<CreateBlog />} />
       <Route path='rate-platform' element={<RatePlatform />} />
       <Route path='my-blog' element={<CheckCreateBlog />} />
       <Route path="/admin-page" element={<AdminPage />} />
       <Route path="/register" element={<RegistrationForm />} />
     </Routes>
     </main>
   </BrowserRouter>
 </div>
  );
}

export default App;