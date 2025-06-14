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
        public DbSet<Interaction> Interactions { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<ChatLog>()
                .Property(c => c.Question)
                .IsRequired();

            modelBuilder.Entity<ChatLog>()
                .Property(c => c.Answer)
                .IsRequired();

            modelBuilder.Entity<Interaction>()
                .Property(i => i.UserId)
                .IsRequired();

            modelBuilder.Entity<Interaction>()
                .Property(i => i.DocumentId)
                .IsRequired();

            modelBuilder.Entity<Interaction>()
                .Property(i => i.Query)
                .IsRequired();

            modelBuilder.Entity<Interaction>()
                .Property(i => i.Response)
                .IsRequired();

            modelBuilder.Entity<Interaction>()
                .Property(i => i.Metadata)
                .IsRequired();
        }
    }
} 