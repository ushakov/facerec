import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomeView } from './views/HomeView';
import { ExploreView } from './views/ExploreView';
import { ComponentView } from './views/ComponentView';
import { CompareView } from './views/CompareView';
import { PeopleView } from './views/PeopleView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomeView />} />
          <Route path="/faces" element={<ExploreView />} />
          <Route path="/faces/:id" element={<ExploreView />} />
          <Route path="/components" element={<ComponentView />} />
          <Route path="/components/:id" element={<ComponentView />} />
          <Route path="/compare/:id1/:id2" element={<CompareView />} />
          <Route path="/people" element={<PeopleView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
