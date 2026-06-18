interface EngLogoProps {
  showHub?: boolean;
}

const LOGO_SRC = '/assets/branding/transparent_eng_logo.png';

export function EngLogo({ showHub = true }: EngLogoProps) {
  return (
    <div className="eng-logo" aria-label="Engineering HR Hub">
      <img
        src={LOGO_SRC}
        alt=""
        className="eng-logo__img"
        width={36}
        height={36}
        aria-hidden
      />
      <span className="eng-logo__hub">eng</span>
      {showHub && (
        <>
          <span className="eng-logo__sep" aria-hidden>
            ┬À
          </span>
          <span className="eng-logo__hub">hr hub</span>
        </>
      )}
    </div>
  );
}
