using System.Text.Json.Serialization;


namespace Core.DTOs
{
    public class UsersDTO
    {
        [JsonPropertyName("id")]
        public Guid ID { get; set; }
        [JsonPropertyName("name")]
        public required string Name { get; set; } 
        [JsonPropertyName("surname")]
        public required string Surname { get; set; }
        [JsonPropertyName("email")]
        public required string Email { get; set; }
        [JsonPropertyName("username")]
        public required string Username { get; set; }
    }

}