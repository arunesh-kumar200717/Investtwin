export default function ReviewRequiredBanner({ title = "Review Recommended", detail = "The Investment Twin detected a meaningful change and the investor should review the updated context." }) {
  return (
    <div className="review-required-banner">
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  );
}
