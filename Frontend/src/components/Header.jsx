function Header({ name, handleLogout }) {
  return (
    <header className="dashboard-header">
      <p className="welcome-text">
        Welcome: <strong>{name}</strong>
      </p>

      <h1 className="dashboard-title">
        UC Merced
      </h1>

      <button
        className="sign-out-button"
        onClick={handleLogout}
      >
        Sign Out
      </button>
    </header>
  );
}

export default Header;