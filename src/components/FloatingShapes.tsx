export default function FloatingShapes() {
  return (
    <div className="shapes">
      <div className="shape torus s1">
        <svg width="130" height="130" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="40" ry="40" stroke="url(#g1)" strokeWidth="7" />
          <ellipse cx="50" cy="50" rx="20" ry="20" stroke="url(#g1)" strokeWidth="5" />
        </svg>
      </div>
      <div className="shape torus s2">
        <svg width="95" height="95" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1b" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="42" ry="30" stroke="url(#g1b)" strokeWidth="6" transform="rotate(30 50 50)" />
          <ellipse cx="50" cy="50" rx="18" ry="12" stroke="url(#g1b)" strokeWidth="4" transform="rotate(30 50 50)" />
        </svg>
      </div>
      <div className="shape torus s5">
        <svg width="80" height="80" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1c" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="40" ry="40" stroke="url(#g1c)" strokeWidth="5" />
        </svg>
      </div>
      <div className="shape mobius s3">
        <svg width="160" height="160" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="g2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <path d="M100 20 C180 40, 180 160, 100 180 C20 160, 20 40, 100 20 Z M100 40 C160 55, 160 145, 100 160 C40 145, 40 55, 100 40 Z" stroke="url(#g2)" strokeWidth="3" />
        </svg>
      </div>
      <div className="shape mobius s4">
        <svg width="120" height="120" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="g2b" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <path d="M100 20 C180 40, 180 160, 100 180 C20 160, 20 40, 100 20 Z" stroke="url(#g2b)" strokeWidth="2.5" />
        </svg>
      </div>
      <div className="shape mobius s6">
        <svg width="90" height="90" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="g2c" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <path d="M100 20 C180 40, 180 160, 100 180 C20 160, 20 40, 100 20 Z M100 40 C160 55, 160 145, 100 160 C40 145, 40 55, 100 40 Z" stroke="url(#g2c)" strokeWidth="2" />
        </svg>
      </div>
      <div className="shape bubble-shape b1" />
      <div className="shape bubble-shape b2" />
      <div className="shape bubble-shape b3" />
      <div className="shape bubble-shape b4" />
      <div className="shape bubble-shape b5" />
      <div className="shape torus s7">
        <svg width="50" height="50" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g2d" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="40" stroke="url(#g2d)" strokeWidth="4" />
        </svg>
      </div>
      <div className="shape torus s8">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1d" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="42" ry="42" stroke="url(#g1d)" strokeWidth="6" />
          <ellipse cx="50" cy="50" rx="18" ry="18" stroke="url(#g1d)" strokeWidth="4" />
        </svg>
      </div>
      <div className="shape mobius s9">
        <svg width="140" height="140" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="g2e" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <path d="M100 20 C180 40, 180 160, 100 180 C20 160, 20 40, 100 20 Z M100 40 C160 55, 160 145, 100 160 C40 145, 40 55, 100 40 Z" stroke="url(#g2e)" strokeWidth="3" />
        </svg>
      </div>
      <div className="shape torus s10">
        <svg width="75" height="75" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1e" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="38" ry="30" stroke="url(#g1e)" strokeWidth="5" transform="rotate(-20 50 50)" />
        </svg>
      </div>
      <div className="shape mobius s11">
        <svg width="110" height="110" viewBox="0 0 200 200">
          <defs>
            <linearGradient id="g2f" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#a78bfa" stopOpacity="0.6" />
              <stop offset="50%" stopColor="#60a5fa" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <path d="M100 20 C180 40, 180 160, 100 180 C20 160, 20 40, 100 20 Z" stroke="url(#g2f)" strokeWidth="2.5" />
        </svg>
      </div>
      <div className="shape torus s12">
        <svg width="60" height="60" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1f" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <circle cx="50" cy="50" r="40" stroke="url(#g1f)" strokeWidth="4" />
        </svg>
      </div>
      <div className="shape torus s13">
        <svg width="90" height="90" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="g1g" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.75" />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.55" />
            </linearGradient>
          </defs>
          <ellipse cx="50" cy="50" rx="42" ry="42" stroke="url(#g1g)" strokeWidth="5" />
          <ellipse cx="50" cy="50" rx="20" ry="20" stroke="url(#g1g)" strokeWidth="3" />
        </svg>
      </div>
      <div className="shape bubble-shape b6" />
      <div className="shape bubble-shape b7" />
      <div className="shape bubble-shape b8" />
    </div>
  );
}
