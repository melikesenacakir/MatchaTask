using Core.Entities;
using Microsoft.EntityFrameworkCore;

namespace Infra.Database
{
    public class ApplicationDB(DbContextOptions options) : DbContext(options)
    {
        public DbSet<Users> Users { get; set; }

        
    }
}