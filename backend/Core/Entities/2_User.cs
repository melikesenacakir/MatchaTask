

namespace Core.Entities
{
    public class User
    {
        public Guid ID { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Surname { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string PhoneNumber { get; set; } = string.Empty;
        public required string Username { get; set; }
        public required string Password { get; set; }
        public string? PicturePath { get; set; } = string.Empty;
        public string? CVPath { get; set; } = string.Empty;
        public bool IsActive { get; set; } = true;
        public Guid? CompanyID { get; set; }
        public Company? Company { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;


        
    }
}