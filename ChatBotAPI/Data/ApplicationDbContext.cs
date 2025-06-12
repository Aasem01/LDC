using Microsoft.EntityFrameworkCore;
using ChatBotAPI.Models;

namespace ChatBotAPI.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<ChatLog> ChatLogs { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<ChatLog>()
                .Property(c => c.Question)
                .IsRequired();

            modelBuilder.Entity<ChatLog>()
                .Property(c => c.Answer)
                .IsRequired();
        }
    }
} 